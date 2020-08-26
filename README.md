# Data Science Quality Project
Detecting frequency, dose, and peripheral information changes between e-scribe directions and sigline texts. 

### Input

- direction_sigline.csv 

    contains relevant prescription inforamtion.
    
    columns: 
    
      ID: text, docupack prescription ID
      PRESCRIPTION_ID: text
      SIG_ID: text
      LINE_NUMBER: integer
      ESCRIBE_DIRECTIONS: text
      SIG_TEXT: text
      NDC: text

- medications.csv 

    contains relevant medication inforamtion.
    
    columns: 
    
      NDC: text
      DESCRIPTION: text
      GSDD_DESC: text



### Output

- results.csv 

    contains relevant prescription inforamtion and corresponding direction changes.
    
    columns: 
    
      ID: text, docupack prescription ID
      PRESCRIPTION_ID: text
      MEDICATION_DESCRIPTION: text
      ESCRIBE_DIRECTIONS: text
      SIG_TEXT: text
      FREQUENCY_CHANGE: boolean
      DOSE_CHANGE: boolean
      PERIPHERAL_CHANGE: boolean
