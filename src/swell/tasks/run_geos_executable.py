# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
from typing import Optional

from swell.tasks.base.task_base import taskBase
from swell.utilities.shell_commands import run_track_log_subprocess

# --------------------------------------------------------------------------------------------------


class RunGeosExecutable(taskBase):

    def execute(self) -> None:

        # Obtain processor information from AGCM.rc
        # Strip is required in case AGCM.rc file was rewritten
        # -----------------------------------------
        agcm_dict = self.geos.parse_rc(self.forecast_dir('AGCM.rc'))
        np = eval(agcm_dict['NX'].strip("'") + '*' + agcm_dict['NY'].strip("'"))

        # Create RESTART folder
        # ---------------------
        if not os.path.exists(self.forecast_dir('RESTART')):
            os.mkdir(self.forecast_dir('RESTART'))

        # Output log file
        # ---------------
        output_log_file = self.forecast_dir('geos_out.log')

        # Path to the GEOS executable
        # ---------------
        geos_executable = 'GEOSgcm.x'
        geos_executable_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'build',
                                            'bin', geos_executable)

        # GEOS source
        # ---------------
        geos_modules = 'g5_modules.sh'
        geos_modules_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'source',
                                         '@env', geos_modules)

        # Run the GEOS executable
        # -----------------------
        self.logger.info('Running '+geos_executable_path+' with '+str(np)+' processors.')

        geos_lib_path = os.path.join(self.experiment_path(), 'GEOSgcm', 'build', 'lib')

        self.run_executable(np, geos_executable_path, geos_modules_path, output_log_file,
                            geos_lib_path)

    # ----------------------------------------------------------------------------------------------

    def run_executable(
        self,
        np: int,
        geos_executable: str,
        geos_modules: str,
        output_log: str,
        geos_lib_path: Optional[str] = None
    ) -> None:

        # Run the GEOS executable
        # -----------------------
        self.logger.info('Running '+geos_executable+' with '+str(np)+' processors.')

        command = f'source {geos_modules} \n' + \
            f'env LD_PRELOAD={geos_lib_path}/libmom6.so:{geos_lib_path}/libcice6.so ' + \
            f'mpirun -np {np} {geos_executable} ' + \
            f'--logging_config logging.yaml'

        # Run command within bash environment
        # -----------------------------------
        run_track_log_subprocess(self.logger, ['/bin/bash', '-c', command], output_log=output_log,
                                 cwd=self.forecast_dir())

# --------------------------------------------------------------------------------------------------
