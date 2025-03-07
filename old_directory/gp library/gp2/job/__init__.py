from .__tmp_dir import TMP_DIR

from .__job import (
    
    # Variables
    start_time,
    run_id,
    jobinfo,
    sysinfo,
    job_output_locations,
    
    # Functions
    success,
    failure

)

# Compatibility
git_hash  = jobinfo.git_hash
job_name  = jobinfo.job_name
job_group = jobinfo.job_group


