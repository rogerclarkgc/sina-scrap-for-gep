from html_screen import PersonalInfo
from html_screen import get_personal_result

fp = open('other.html', 'r', encoding='utf-8')
personal_page = fp.read()
personal_dev = get_personal_result(personal_page)
fp.close()

Pinfo = PersonalInfo(personal_dev)
frames = Pinfo.get_basic_frame()
print(frames)

all_info = Pinfo.get_all_info()
#info = Pinfo.get_personal_info(frames)
#contact = Pinfo.get_contact_info(frames)
#education = Pinfo.get_education_info(frames)
#work = Pinfo.get_work_info(frames)

print(all_info)
#print(dict(info, **contact, **education, **work))