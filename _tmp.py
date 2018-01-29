
import os
for root, dirs, files in os.walk('D:/Works/Arrangement/MyBands_temp'):
    #         for f in files:
    #             if f[:4] == "MAQE":
    #                 old = os.path.join(root, f)
    #                 new = os.path.join(root, f[:3] + f[4:])
    #                 os.rename(old, new)
    #                 print(old, new)

    for dir in dirs:
        print(dir)
        if dir == 'Final':
            old = os.path.join(root, dir)
            new = os.path.join(root, "FINALS")
            os.rename(old, new)
            print(old, new)
        if dir == 'PDF':
            old = os.path.join(root, dir)
            new = os.path.join(root, "PRINTABLES")
            os.rename(old, new)
            print(old, new)
        if dir == 'MID':
            old = os.path.join(root, dir)
            new = os.path.join(root, "AUDIOS")
            os.rename(old, new)
            print(old, new)
        if dir == 'MUS':
            old = os.path.join(root, dir)
            new = os.path.join(root, "EDITABLES")
            os.rename(old, new)
            print(old, new)
