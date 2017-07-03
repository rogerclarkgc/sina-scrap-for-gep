# coding:utf-8
import re

from bs4 import BeautifulSoup

from fetch_page import get_search_page, get_user_page

def get_search_result(page):
    """
    Got the raw html code from json
    :param page: the html returned by fetch_page.get_search_page
    :return: the html code, a str object, if return None object, it means cannot find
    result
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
    return None

def get_personal_result(page):
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

def reconstruct_weibo(weibo_list, info_list, weibotime=None):
    if len(weibo_list) != len(info_list):
        return []
    else:
        for index in range(0, len(weibo_list)):
            weibo_list[index]['info'] = info_list[index]
            weibo_list[index]['time'] = weibotime
    return weibo_list


class Weibo(object):
    """
    screen weibo content and reconstruct it
    """

    def __init__(self, search_result=None):

        self.status = 'INITIATE'
        self.frame_pattern = 'feed_content wbcon'
        self.nickname_pattern = 'name_txt W_fb'
        self.comment_pattern = 'comment_txt'
        self.userurl_pattern = self.nickname_pattern
        if search_result:
            self.soup = BeautifulSoup(search_result, 'html.parser')
            self.status = 'OK'
        else:
            self.soup = None
            self.status = 'NO_HTML'

    def get_weibo(self):
        frames = self.get_weibo_frame()
        all = []
        if frames != 'NO_FRAME':
            for frame in frames:
                nick_name = self.get_nick_name(frame)
                comment = self.get_weibo_comment(frame)
                user_main = self.get_user_url(frame)
                user_id = self.get_user_id(frame)
                weibo = {'nick_name': nick_name,
                        'comment': comment,
                        'user_main': user_main,
                        'user_id': user_id,
                        'info': None}
                all.append(weibo)
        return all

    def get_weibo_frame(self):
        try:
            frames = self.soup.find_all(class_=self.frame_pattern)
        except AttributeError as e:
            return 'NO_FRAME'
        if len(frames) <= 0:
            return 'NO_FRAME'
        return frames

    def get_nick_name(self, frame):
        try:
            nick_name = frame.find(class_=self.nickname_pattern)['nick-name']
        except (KeyError, TypeError, AttributeError) as e:
            nick_name = 'NO_NICK'
        return nick_name

    def get_weibo_comment(self, frame):
        try:
            comment = frame.find(class_=self.comment_pattern).text
        except AttributeError:
            comment = 'NO_COMMENT'
        return comment


    def get_user_url(self, frame):
        try:
            user_main = frame.find(class_=self.userurl_pattern)['href']
        except (KeyError, TypeError, AttributeError) as e:
            user_main = 'NO_USERMAIN'
        return user_main

    def get_user_id(self, frame):
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




class WeiboInfo(object):

    def __init__(self, search_result=None):
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
        try:
            weibo_infoframes = self.soup.find_all(class_=self.infoframe_pattern)
        except AttributeError as e:
            return 'NO_INFOFRAME'
        if len(weibo_infoframes) <= 0:
            return 'NO_INFOFRAME'
        return weibo_infoframes

    def get_weibo_infolist(self, frame):
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
                          'orientation': '性取向：',
                          'email': '邮箱：',
                          'qq': 'QQ：',
                          'msn': 'MSN：',
                          }
        if personal_result:
            self.soup = BeautifulSoup(personal_result, 'html.parser')
            self.status = 'OK'
        else:
            self.soup = None
            self.status = 'NO_HTML'

    def get_basic_frame(self):
        try:
            frames = self.soup.find_all('h2')
        except AttributeError as e:
            return 'NO_FRAME'
        if len(frames) <= 0:
            return 'NO_FRAME'
        return frames

    def get_personal_info(self, frames):
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
                else:
                    #print('!!!')
                    continue
            node = ''
            while str(node).__contains__('clearfix') is False:
                node = next(g)
            li = node.find_all('li')
            if len(li) <= 0:
                return 'NO_PERSONAL_LI'
            for tag in li:
                for item in self.infomodel.items():
                    if item[1] in tag.text:
                        info[item[0]] = tag.find('span', class_='pt_detail').text

            return info

        else:
            return {}


if __name__ == '__main__':
    r = get_search_page(keyword='大熊猫',
                        start='2017-1-1',
                        end='2017-7-3',
                        page=1)
    sr = get_search_result(r)
    w = Weibo(sr)
    w_info = WeiboInfo(sr)
    info_list = w_info.get_weibo_info()
    w_list = w.get_weibo()
    all_weibo = reconstruct_weibo(w_list, info_list, '2017')
    for i in all_weibo:
        print(i)
    user_page = get_user_page(all_weibo[3]['user_id'])
    user_content = get_personal_result(user_page)
    print(user_content)

    Person = PersonalInfo(user_content)
    frames = Person.get_basic_frame()
    info = Person.get_personal_info(frames)
    print(info)
    #fp = open('user_content.html', 'w', encoding='utf-8')
    #fp.write(user_content)
    #fp.close()


    #print(soup)
    #print(sr)
    #soup.prettify()
