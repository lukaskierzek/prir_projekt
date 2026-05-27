from pathlib import Path
import shutil


def find_mpiexec() -> str | None:
    mpiexec = shutil.which("mpiexec")
    if mpiexec:
        return mpiexec

    windows_mpi = Path(r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe")
    if windows_mpi.exists():
        return str(windows_mpi)

    return None
