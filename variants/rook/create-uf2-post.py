import os

Import("env")

def create_uf2(source, target, env):
    firmware_hex = os.path.join(env.subst("$BUILD_DIR"), "firmware.hex")
    uf2_file = os.path.join(env.subst("$BUILD_DIR"), "firmware.uf2")
    uf2conv = os.path.join(env.subst("$PROJECT_DIR"), "bin", "uf2conv", "uf2conv.py")
    env.Execute(
        '"$PYTHONEXE" "%s" -f 0xADA52840 -c "%s" -o "%s"' % (uf2conv, firmware_hex, uf2_file)
    )

env.AddPostAction("$BUILD_DIR/${PROGNAME}.hex", create_uf2)
