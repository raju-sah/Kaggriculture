from main import _KAZUHIRO_ACTIONS, _NAM_ACTIONS

diff_step = -1
for i, (k, n) in enumerate(zip(_KAZUHIRO_ACTIONS, _NAM_ACTIONS)):
    if k != n:
        diff_step = i
        break

print(f"First difference at step: {diff_step}")
if diff_step != -1:
    print("KAZUHIRO:", _KAZUHIRO_ACTIONS[diff_step])
    print("NAM     :", _NAM_ACTIONS[diff_step])
