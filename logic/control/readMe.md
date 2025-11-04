## Control system plans:
Goal is to produce a control system to update suspension in real time to improve suspension performance\
By changing compression and rebound speeds for fork and shock\
Using key metrics as features from dict in accelerometer_data_processor

### Primitive solution: 
Align fork and shock regression values to improve bike balance.

### Classification model to ride type
Use key metrics as features to classify ride states\
Such as: (Jumps / no jumps), (rocky, smooth, sand, gravel, ect.)

### Regression model
Predict continuous measures of terrain/ride state\
Such as (uphill - downhill), (smooth - rocky)

### Metadata needed from runs:
