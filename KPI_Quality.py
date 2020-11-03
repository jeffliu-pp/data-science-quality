#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 16:19:50 2020

Quality Project

@author: liujianf
"""

import os
import pandas as pd
from datetime import datetime, timedelta 

###############################################################################
# SQL
def _SQL(QUERY):
    import data_science_tools as dst
    snow_eng = dst.snowflake_prod
    snow_conn = snow_eng.connect()
    data = pd.read_sql(QUERY, con=snow_conn)
    snow_conn.close()
    snow_eng.dispose()
    return data

def _QUERY(TIME1, TIME2):
    QUERY = """WITH 
               -------------------
               doc2first_return_time AS ( 
               SELECT DOCUMENT_ID, MIN(
               CASE WHEN 
               ((MOVED_TO_QUEUE = 'DataEntry') AND (ACTION = 'Transitioned') AND (CURRENT_QUEUE = 'RphCheck'))
               THEN CREATED_AT ELSE TO_TIMESTAMP_TZ('2030-01-01T12:00:00.000+00:00') END) 
               FIRST_RETURNED_TO_DE_AT
               FROM source_pillpack_core.docupack_document_histories
               GROUP BY DOCUMENT_ID
               ),
               --------------------
               audit_data AS(
               -- real-time data
               SELECT    
               doc_pres.id id,
               sig.prescription_id,
               sig.id sig_id,
               sig.line_number,
               sig.text sig_text,
               esc.message_json:MedicationPrescribed.SigText::string directions,  -- Updated 2020-10-15 due to new doucpack_escribes table
               esc.message_json:MedicationPrescribed.NDC ndc,                     -- Updated 2020-10-15 due to new doucpack_escribes table
               sig.quantity_per_dose,
               sig.units,
               sig.hoa_times,
               sig.quantity_per_day,
               sig.schedule_type,
               sig.period,
               sig.dow,
               doc_pres.med_name medication_description,
               docs.queue current_queue,
               ('https://admin.pillpack.com/admin/docupack/#/' || docs.id) docupack_url
               FROM source_pillpack_core.docupack_prescriptions doc_pres
               LEFT JOIN source_pillpack_core.docupack_documents docs ON doc_pres.document_id = docs.id
               LEFT JOIN source_pillpack_core.prescriptions pres ON doc_pres.app_prescription_id = pres.id
               LEFT JOIN source_pillpack_core.sig_lines sig ON doc_pres.app_prescription_id = sig.prescription_id
               LEFT JOIN source_pillpack_core.docupack_escribes esc ON esc.id= doc_pres.INBOUND_ESCRIBE_ID          -- Updated 2020-10-15 due to new doucpack_escribes table
               LEFT JOIN doc2first_return_time ON docs.id = doc2first_return_time.DOCUMENT_ID     --###
               WHERE    
               pres.created_at >= '{0}T08:15:00.000+00:00'   -- query run time minus 24 hours
               AND pres.created_at < '{1}T08:15:00.000+00:00'    -- query run time
               AND  ((docs.entered_rph_check_at is null) or 
                     ( (doc2first_return_time.FIRST_RETURNED_TO_DE_AT > '{1}T08:15:00.000+00:00') AND (docs.entered_rph_check_at> '{1}T08:15:00.000+00:00') ) 
                     ) -- query run time  --###
               AND sig.id IS NOT NULL
               AND       pres.rx_number IS NOT NULL
               AND       doc_pres.self_prescribed = false
               AND       docs.source = 'Escribe'
               AND       directions is NOT NULL 
               ),
               ----------------------------------------------------
               near_miss_data AS (SELECT
               DOCUPACK_ERRORS.PRESCRIPTION_ID AS docupack_prescriptions_id,
               max(CASE WHEN (
                    (DOCUPACK_ERRORS.category like '%sig%') AND 
                       (DOCUPACK_ERRORS.name like '%directions%') 
                  ) 
               THEN True ELSE False END) contains_sig_error
               FROM SOURCE_PILLPACK_CORE.DOCUPACK_ERRORS
               GROUP BY docupack_prescriptions_id)
               --------------------------------------------------------------    
               SELECT audit_data.*
               FROM audit_data 
               LEFT JOIN near_miss_data ON audit_data.id = near_miss_data.docupack_prescriptions_id
               WHERE near_miss_data.contains_sig_error = True""".format(TIME1,TIME2)
    return QUERY

###############################################################################

###############################################################################
# Send email from SES that the job failed to run
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

EMAIL_LIST = ['jeff.liu@pillpack.com'] #, 'cetinkay@amazon.com', 'mohsen.bayati@pillpack.com', 'ipshita.jain@pillpack.com', 'olivia@pillpack.com', 'dane@pillpack.com', 'colin.hayward@pillpack.com']

class EmailClient:
    def __init__(self, sender="data_science_bot@pillpack.com", region="us-east-1"):
        self.sender = sender
        self.client = boto3.client('ses',region_name=region)

    def construct_email(self, subject, body):
        body_html = """
        <html>
        <head></head>
        <body>
          <h1>{0}</h1>
          <p>{1}</p>
        </body>
        </html>
        """.format(subject, body)
        return body_html

    def send_email(self, recipients, subject, body, attachment=None, charset="utf-8"):
        body_html = self.construct_email(subject, body)
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(recipients)
        # message body
        part = MIMEText(body_html.encode(charset), 'html', charset)
        msg.attach(part)
        if attachment:
            # attachment
            part = MIMEApplication(open(attachment, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename='Direction_Changes_'+pd.to_datetime('now').date().isoformat()+'.csv')
            msg.attach(part)
        response = self.client.send_raw_email(
            Source=msg['From'],
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )
###############################################################################


###############################################################################
def main():
    # Path and Filename
    PATH = os.path.abspath(os.getcwd())#+'/Data/'
    results = {}
    START_TIME = (pd.to_datetime('now') - timedelta(days=8)).date().isoformat()
    END_TIME = (pd.to_datetime('now') - timedelta(days=1)).date().isoformat()
    OUTPUT = '/Results/KPI_'+START_TIME+'_'+END_TIME+'.csv'
    for d in range(1,8):
        TIME2 = (pd.to_datetime('now') - timedelta(days=d)).date().isoformat()
        TIME1 = (pd.to_datetime('now') - timedelta(days=d+1)).date().isoformat()
        data = pd.read_csv(PATH+'/Results/results_'+TIME2+'.csv' )
        ss = pd.read_csv(PATH+'/Results/snapshots_'+TIME2+'.csv')
        print('Running SQL to pull near misses from Snowflake...') 
        nm = _SQL(_QUERY(TIME1, TIME2))                          
        nm.columns = nm.columns.str.upper()
        new = nm.merge(ss, on=['ID','PRESCRIPTION_ID'], how='left')
        new = new.merge(data, on=['ID','PRESCRIPTION_ID'], how='left')
        new = new.rename(columns={'SIG_TEXT_x':'NEW_SIG_TEXT','SIG_TEXT_y':'ORIGINAL_SIG_TEXT', 'TOTAL_LINE_COUNT_x': 'TOTAL_LINE_COUNT'})
        if len(results) == 0:
            results = new
        else:
            results = pd.concat([results, new], sort=False)
    results[['ID','PRESCRIPTION_ID','LINE_NUMBER','TOTAL_LINE_COUNT', 'DIRECTIONS', 'NEW_SIG_TEXT','ORIGINAL_SIG_TEXT',
             'DOSE_CHANGE','FREQUENCY_CHANGE','PERIPHERAL_CHANGE']].to_csv(PATH+OUTPUT,index=False)
    email = EmailClient()
    email.send_email(EMAIL_LIST,
       'Direction Changes KPI ' + START_TIME + ' ' + END_TIME,
       'Hey team, <br><br>\
       Attached please find the direction change KPI from {0} to {1}. If you have any questions please contact Jeff Liu: jeff.liu@pillpack.com. <br><br> \
       Key Columns: <br> \
       ID: docupack prescriptions id <br> \
       PRESCRIPTION_ID <br> \
              LINE_NUMBER: sigline number <br> \
       TOTAL_LINE_COUNT: total number of siglines; if a prescription has more than one siglines, it is likely to be detected since information is saved in different siglines <br> \
       DIRECTIONS: escribe directions <br> \
       NEW_SIG_TEXT: correct sig text after RPH check <br> \
       ORIGINAL_SIG_TEXT: original sig text before correction <br> \
       DOSE_CHANGE: if Ture, there are changes; if False, dose info is missing <br> \
       FREQUENCY_CHANGE: if Ture, there are changes; if False, frequency info is missing <br> \
       PERIPHERAL_CHANGE: if Ture, there are changes <br><br>\
       Best, <br>data_science_bot'.format(START_TIME, END_TIME),
       PATH+OUTPUT)
    return results

if __name__ == "__main__":
    results = main()
