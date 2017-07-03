from html_screen import PersonalInfo

fp = open('personal_result_dev.html', 'r', encoding='utf-8')
personal_dev = fp.read()
fp.close()

Pinfo = PersonalInfo(personal_dev)
frames = Pinfo.get_basic_frame()
print(frames)

info = Pinfo.get_personal_info(frames)

print(info)