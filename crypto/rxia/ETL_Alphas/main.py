"""
********************************************************************************
Description: SQL production process runner
      Usage: Runs the Alpha process but outlier removals will 
             need to be manually removed
     Author: Xia, Redmond
    Created: 2021-05-05
********************************************************************************
"""



import gp.job
import gp.runner

gp.runner.run_steps()
gp.job.success()