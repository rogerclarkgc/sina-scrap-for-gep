# coding:utf-8
import re
import time
from base64 import encodebytes

from bs4 import BeautifulSoup

from fetch_page import get_search_page, get_user_page
import basic
# TODO: 需要统一各个模块之间异常处理之间接口的一致性和通用性
# TODO: 需要整合各个模块异常消息传递机制，统一写入消息日志
def get_search_result(page):
    """
    Got the raw html code from json
    :param page: the html returned by fetch_page.get_search_page
    :return: the html code, a str object, if return None object, it means cannot find the html
    """
    view_pattern = r'view\((.*)\)'
    html_pattern = r'"html":"(.*)"}$'
    soup = BeautifulSoup(page, 'html.parser')
    scripts = soup.find_all('script')
    pattern = re.compile(view_pattern)
    for script in scripts:
        m = pattern.search(str(script))
        if m and 'pl_weibo_direct' in script.string and 'S_txt1' in script.string:
            search_cont = m.group(1)
            pattern2 = re.compile(html_pattern)
            m2 = pattern2.search(search_cont)
            if m2:
                # FIXME: 出现编码错误'utf-8' codec can't encode characters in position 103-104: surrogates not allowed
                # FIXME: 目前无法确认错误原因，可能是原文中的一些字符导致的问题
                return m2.group(1).encode('utf-8', 'ignore').decode('unicode-escape', 'ignore').replace('\\', '')
                #return m2.group(1)
            else:
                continue
        else:
            continue
    return None

def get_personal_result(page):
    """
    Got the raw html code from json where contain in the <script> tag
    :param page:the html str object, returned by fetch_page.get_user_page
    :return:the html code, if return None object, it means cannot find the html
    """
    view_pattern = r'view\((.*)\)'
    html_pattern = r'"html":"(.*)"}$'
    if page == 'PUBLIC_ACCOUNT':
        print('当前页面为公众号，跳过抓取个人信息！')
        return None
    else:
        soup = BeautifulSoup(page, 'html.parser')
        scripts = soup.find_all('script')
        pattern = re.compile(view_pattern)
        for script in scripts:
            m = pattern.search(str(script))
            if m and 'PCD_text_b' in script.string:
                person_cont = m.group(1)
                pattern2 = re.compile(html_pattern)
                m2 = pattern2.search(person_cont)
                if m2:
                    #return m2.group(1)
                    return m2.group(1).encode('utf-8', 'ignore').decode('utf-8', 'ignore').replace('\\', '')
        return None

def reconstruct_weibo(weibo_list, info_list):
    if len(weibo_list) != len(info_list):
        return []
    else:
        for index in range(0, len(weibo_list)):
            weibo_list[index]['info'] = info_list[index]
    return weibo_list


class Weibo(object):
    """
    screen weibo content and reconstruct it
    """

    def __init__(self, search_result=None):
        """
        initiate the class
        :param search_result: must be the result of function html_screen.get_search_result
        """
        self.status = 'INITIATE'    # the status code of screen process
        self.frame_pattern = 'content clearfix'
        self.nickname_pattern = 'name_txt W_fb'
        self.comment_pattern = 'comment_txt'
        self.timestamp_pattern = 'W_textb'
        self.userurl_pattern = self.nickname_pattern
        if search_result:
            self.soup = BeautifulSoup(search_result, 'html.parser')
            self.status = 'OK'
        else:
            self.soup = None
            self.status = 'NO_HTML'

    def get_weibo(self):
        """
        get all weibo content in a search page
        :return: a list object, default length is 20, contain 20 weibo content, every content is a dict object
        """
        frames = self.get_weibo_frame()
        all = []
        if frames != 'NO_FRAME':
            for frame in frames:
                nick_name = self.get_nick_name(frame)
                comment = self.get_weibo_comment(frame)
                user_main = self.get_user_url(frame)
                user_id = self.get_user_id(frame)
                timestamp = self.get_timestamp(frame)
                if len(comment) > 5:
                    stamp = encodebytes((user_id+comment[0:5]).encode(errors='ignore'))
                else:
                    stamp = encodebytes((user_id+comment[0:2]).encode(errors='ignore'))
                weibo = {'i_stamp': stamp,
                         'timestamp': timestamp,
                         'nick_name': nick_name,
                         'comment': comment,
                         'user_main': user_main,
                         'user_id': user_id,
                         'info': None}
                all.append(weibo)
        return all

    def get_weibo_frame(self):
        """
        get the frame of weibo, because the default search result is 20weibo/page, there are 20 frames
        :return: a list of frames
        """
        try:
            frames = self.soup.find_all(class_=self.frame_pattern)
        except AttributeError as e:
            return 'NO_FRAME'
        if len(frames) <= 0:
            return 'NO_FRAME'
        return frames

    def get_nick_name(self, frame):
        """
        get the nick_name of user
        :param frame: must be the element of html_screen.Weibo.get_weibo_frame's return value
        :return: a str object, which is the nick name of the weibo user
        """
        try:
            nick_name = frame.find(class_=self.nickname_pattern)['nick-name']
        except (KeyError, TypeError, AttributeError) as e:
            nick_name = 'NO_NICK'
        return nick_name

    def get_weibo_comment(self, frame):
        """
        get the weibo comment
        :param frame: must be the element of html_screen.Weibo.get_weibo_frame's return value
        :return: a str object
        """
        try:
            comment = frame.find(class_=self.comment_pattern).text
        except AttributeError:
            comment = 'NO_COMMENT'
        return comment


    def get_user_url(self, frame):
        """
        get the user's main persnal page
        :param frame: must be the element of html_screen.Weibo.get_weibo_frame's return value
        :return: a str object, actually it is the url of main page
        """
        try:
            user_main = frame.find(class_=self.userurl_pattern)['href']
        except (KeyError, TypeError, AttributeError) as e:
            user_main = 'NO_USERMAIN'
        return user_main

    def get_user_id(self, frame):
        """
        get the user's id
        :param frame: must be the element of html_screen.Weibo.get_weibo_frame's return value
        :return: a str object , the unique weibo id for everyuser
        """
        try:
            user_card = frame.find(class_=self.userurl_pattern)['usercard']
            find = re.search(r'id=(\d{1,11})&', user_card)
            if find:
                user_id = find.group(1)
            else:
                user_id = 'NO_USERID'
        except (KeyError, TypeError, AttributeError) as e:
            user_id = 'NO_USERID'
        return user_id

    def get_timestamp(self, frame):
        """
        get the weibo's time
        :param frame: must be the element of html_screen.Weibo.get_weibo_frame's return value
        :return: a str object, the time of weibo
        """
        try:
            timestamp_raw = frame.find('a', class_=self.timestamp_pattern)['date']
            find = re.search(r'(\d{0,10})000', timestamp_raw)
            if find:
                timestamp = find.group(1)
                timestamp_str = time.strftime('%Y-%m-%d %X', time.gmtime(int(timestamp)))
            else:
                timestamp_str = 'NO_TIMESTAMP'
        except (KeyError, TypeError, AttributeError) as e:
            timestamp_str = 'NO_TIMESTAMP'
        return timestamp_str






class WeiboInfo(object):
    """
    screen the weibo's basic info and reconstruct it by dict object
    """

    def __init__(self, search_result=None):
        """
        initiate the class
        :param search_result: must be the result of function html_screen.get_search_result
        """
        self.infoframe_pattern = 'feed_action_info feed_action_row4'
        self.infolist_patter = 'li'
        self.reg_pattern = r'.*(\d)'
        self.status = 'INITIATE'
        if search_result:
            self.soup = BeautifulSoup(search_result, 'html.parser')
            self.status = 'OK'
        else:
            self.soup = None
            self.status = 'NO_HTML'

    def get_weibo_info(self):
        """
        reconstruct the weibo info, including favorite, forward, comment and praise
        :return:a list object, default length is 20
        """
        infoframes = self.get_weibo_infoframe()
        all = []
        if infoframes != 'NO_INFOFRAME':
            for frame in infoframes:
                all_info = self.get_weibo_infolist(frame)
                if all_info != 'NO_INFOLIST':
                    info_dict = {'favorite': all_info[0],
                                'forward': all_info[1],
                                'comment': all_info[2],
                                'praise': all_info[3]}
                else:
                    info_dict = {'favorite': 'ERROR',
                                 'forward': 'ERROR',
                                 'comment': 'ERROR',
                                 'praise': 'ERROR'}
                all.append(info_dict)
        return all

    def get_weibo_infoframe(self):
        """
        get the weibo's infoframe, the default length is 20
        :return: a list object of infoframes
        """
        try:
            weibo_infoframes = self.soup.find_all(class_=self.infoframe_pattern)
        except AttributeError as e:
            return 'NO_INFOFRAME'
        if len(weibo_infoframes) <= 0:
            return 'NO_INFOFRAME'
        return weibo_infoframes

    def get_weibo_infolist(self, frame):
        """
        get the weibo's info list
        :param frame: must be a element of a list object which returned by html_screen.WeiboInfo.get_weibo_infoframe
        :return: a list object, which contained the info of a weibo
        """
        try:
            info_list = frame.find_all('li')
        except AttributeError as e:
            return 'NO_INFOLIST'
        if len(info_list) <= 0:
            return 'NO_INFOLIST'
        fav_res = re.search(self.reg_pattern, info_list[0].text)
        fow_res = re.search(self.reg_pattern, info_list[1].text)
        cmt_res = re.search(self.reg_pattern, info_list[2].text)
        pra_res = info_list[3].text
        if fav_res:
            fav = int(fav_res.group(1))
        else:
            fav = 0
        if fow_res:
            fow = int(fow_res.group(1))
        else:
            fow = 0
        if cmt_res:
            cmt = int(cmt_res.group(1))
        else:
            cmt = 0
        if pra_res:
            pra = int(pra_res)
        else:
            pra = 0
        return [fav, fow, cmt, pra]


class PersonalInfo(object):
    def __init__(self, personal_result=None):
        """
        initiate the object
        :param personal_result:the return value of get_personal_result
        """
        self.status = 'INITITATE'
        self.frame_pattern = 'h2'
        self.infomodel = {'true_name': '真实姓名：',
                          'location': '所在地：',
                          'gender': '性别：',
                          'birthday': '生日：',
                          'orientation': '性取向：'
                          }
        self.contactmodel = {'email': '邮箱：',
                             'qq': 'QQ：',
                             'MSN': 'MSN：'}
        self.workmodel = {'company': '公司：'}
        self.educationmodel = {'university': '大学：',
                               'highschool': '高中：',
                               'vocation': '高职：',
                               'junior': '初中：',
                               'technical': '中专技校',
                               'primary': '小学',
                               'oversea': '海外'}
        if personal_result:
            self.soup = BeautifulSoup(personal_result, 'html.parser')
            self.status = 'OK'
        else:
            self.soup = None
            self.status = 'NO_HTML'

    def get_all_info(self):
        """
        reconstruct all info with a dict object
        :return:a dict object which contain all info, the default value of every info is 'None'
        """
        frames = self.get_basic_frame()
        personal_info = self.get_personal_info(frames)
        contact_info = self.get_contact_info(frames)
        work_info = self.get_work_info(frames)
        education_info = self.get_education_info(frames)
        all_info = dict(personal_info, **contact_info, **work_info, **education_info)
        return all_info

    def get_basic_frame(self):
        """
        get the basic frame of personal info page, normally, therer are 4 frames:
        '基本信息'\'联系信息'\'工作信息'\'教育信息'
        :return: a list object, contained all frames in the personal page
        """
        try:
            frames = self.soup.find_all('h2')
        except AttributeError as e:
            return 'NO_FRAME'
        if len(frames) <= 0:
            return 'NO_FRAME'
        return frames

    def get_personal_info(self, frames):
        """
        get the info from ‘个人信息’ frame
        :param frames: must be a list object, returned by html_screen.PersonalInfo.get_basic_frame()
        :return: a dict object, a user's personal info
        """
        info = {'true_name': 'None',
                'location': 'None',
                'gender': 'None',
                'birthday': 'None',
                'orientation': 'None',
                'email': 'None',
                'qq': 'None',
                'msn': 'None',
                }
        if frames != 'NO_FRAME':
            for frame in frames:
                if '基本信息' in frame.text:
                    g = frame.next_elements
                    break
                else:
                    g = 'NO_INFO'
            if g == 'NO_INFO':
                return info
            node = ''
            while str(node).__contains__('clearfix') is False:
                node = next(g)
            li = node.find_all('li')
            if len(li) <= 0:
                return info
            for tag in li:
                for item in self.infomodel.items():
                    if item[1] in tag.text:
                        info[item[0]] = tag.find('span', class_='pt_detail').text

            return info

        else:
            return info

    def get_contact_info(self, frames):
        """
        get the info from '联系信息' frame
        :param frames: must be a list object, returned by html_screen.PersonalInfo.get_basic_frame()
        :return: a dict object, a user's contact info
        """
        contact = {'email': 'None',
                   'qq': 'None',
                   'MSN':'None'}
        if frames != 'NO_FRAME':
            for frame in frames:
                if '联系信息' in frame.text:
                    g = frame.next_elements
                    break
                else:
                    g = 'NO_CONTACT'
            if g == 'NO_CONTACT':
                return contact
            node = ''
            while str(node).__contains__('clearfix') is False:
                node = next(g)
            li = node.find_all('li')
            if len(li) <= 0:
                return contact
            for tag in li:
                for item in self.contactmodel.items():
                    if item[1] in tag.text:
                        contact[item[0]] = tag.find('span', class_='pt_detail').text
            return contact
        else:
            return contact

    def get_work_info(self, frames):
        """
        get the info from '工作信息' frame
        :param frames: must be a list object, returned by html_screen.PersonalInfo.get_basic_frame()
        :return: a dict object, a user's work info
        """
        work = {'company': 'None'}
        if frames != 'NO_FRAME':
            for frame in frames:
                if '工作信息' in frame.text:
                    g = frame.next_elements
                    break
                else:
                    g = 'NO_WORK'
            if g == 'NO_WORK':
                return work
            node = ''
            while str(node).__contains__('clearfix') is False:
                node = next(g)
            li = node.find_all('li')
            if len(li) <= 0:
                return work
            for tag in li:
                for item in self.workmodel.items():
                    if item[1] in tag.text:
                        work[item[0]] = tag.find('a').text
            return work
        else:
            return work

    def get_education_info(self, frames):
        """
        get info from '教育信息' frame
        :param frames: must be a list object, returned by html_screen.PersonalInfo.get_basic_frame()
        :return: a user's education info
        """
        education = {'university': 'None',
                               'highschool': 'None',
                               'vocation': 'None',
                               'junior': 'None',
                               'technical': 'None',
                               'primary': 'None',
                               'oversea': 'None'}
        if frames != 'NO_FRAME':
            for frame in frames:
                if '教育信息' in frame.text:
                    g = frame.next_elements
                    break
                else:
                    g = 'NO_EDUCATION'
            if g == 'NO_EDUCATION':
                return education
            node = ''
            while str(node).__contains__('clearfix') is False:
                node = next(g)
            li = node.find_all('li')
            if len(li) <= 0:
                return education
            for tag in li:
                for item in self.educationmodel.items():
                    if item[1] in tag.text:
                        education[item[0]] = tag.find('a').text
            return education
        else:
            return education

    def get_tag_info(self, frames):
        # TODO: 用于抓取标签信息
        pass






if __name__ == '__main__':
    r = get_search_page(keyword='大熊猫',
                        start='2017-1-1',
                        end='2017-7-5',
                        page=1,
                        owner='xie')
    sr = get_search_result(r)
    print('next:', basic.is_next(sr))
    w = Weibo(sr)
    w_info = WeiboInfo(sr)
    info_list = w_info.get_weibo_info()
    w_list = w.get_weibo()
    all_weibo = reconstruct_weibo(w_list, info_list)
    for i in all_weibo:
        print(i)
    print('waiting...')
    time.sleep(5)
    user_page = get_user_page(all_weibo[7]['user_id'], owner='xie')
    user_content = get_personal_result(user_page)
    print(user_content)

    Person = PersonalInfo(user_content)
    all_info = Person.get_all_info()
    print(all_info)
    #fp = open('user_content.html', 'w', encoding='utf-8')
    #fp.write(user_content)
    #fp.close()


    #print(soup)
    #print(sr)
    #soup.prettify()
