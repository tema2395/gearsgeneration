from cx_Freeze import setup, Executable

setup(
    name="gearsgen",
    version="1.0",
    description="Gears Generation Application",
    executables=[Executable("main.py", base="Win32GUI")]
)
