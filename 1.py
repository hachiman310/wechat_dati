import os
import random
import time
from PIL import Image
from paddleocr import PaddleOCR, draw_ocr
import pymysql

old_text=''
s=''

while (1):
    file_name = int(time.time())
    os.system('adb shell screencap -p /sdcard/%d.png' % file_name)
    os.system('adb pull /sdcard/%d.png ./pig/' % file_name)

    img = Image.open("./pig/%d.png" % file_name)
    # 切割问题区域
    # (起始点的横坐标，起始点
    # 的纵坐标，宽度，高度）
    question = img.crop((140, 530, 1300, 800))
    # 保存问题区域
    question.save("./pig/question%d.png" % file_name)

    ocr = PaddleOCR(use_angle_cls=False,
                    lang="ch",
                    show_log=False
                    )  # need to run only once to download and load model into memory
    img_path = "./pig/question%d.png" % file_name
    result = ocr.ocr(img_path, cls=False)
    # 获取题目文本
    try:
        typ1e= [line[0][1] for line in result]
        s=typ1e[0][0]
        s=s[1:-1]
        print(s)
    except:
        s=''
    try:
        questionList1 = [line[1][1] for line in result]
        questionList2 = [line[2][1] for line in result]
        questionList3 = [line[3][1] for line in result]
        # print(questionList)
        text = questionList1[0][0]+questionList2[0][0]+questionList3[0][0]
    except:
        try:
            questionList1 = [line[1][1] for line in result]
            questionList2 = [line[2][1] for line in result]
            # print(questionList)
            text = questionList1[0][0]+questionList2[0][0]
            
        except Exception as e:
            questionList1 = [line[1][1] for line in result]
            text = questionList1[0][0]
    # text=text[2:-3]
    print(text)
    if(old_text==text ):
        time.sleep(2)
        continue
        
    old_text=text
    db = pymysql.connect(host='localhost',
                         user='root',
                         password='123456',
                         database='qanda')
    cursor = db.cursor()
    if(s=='判断' or s=='多选'):
        sql = """SELECT question,right_ans,type,id,right_point,point_xy,click_xy FROM `sheet1` where question like '% """+text+"""%' and type = '"""+s+"""'"""
        
    else:
        sql = """SELECT question,right_ans,type,id,right_point,point_xy,click_xy FROM `sheet1` where question like '"""+text+"""%'"""
    cursor.execute(sql)
    print(sql)

    # 使用 fetchone() 方法获取单条数据.
    what_i_want=""
    what_point_num=''
    what_point_xy=''
    what_click=''
    if cursor is not None:
        row = cursor.fetchall()
        if len(row)>0:
            for k in row:
                qus = k[0]
                what_i_want = k[1]
                what_type_want = k[2]
                what_id= k[3]
                what_point_num = k[4]
                what_point_xy = k[5]
                what_click=k[6]
                print("-------------------------------------------------------")
                print("问题是:\033[32m"+str(what_id)+"-:-"+what_type_want+"-:-"+qus+"\033[0m")
                print("\033[1;31;41m 正确答案是:%s \033[0m" % what_i_want) 
                print("-------------------------------------------------------")
        else:
            print("请输入是否保存：1是|0否")
            ye1s=input()
            if(ye1s=='1'):
                print("输入类型回车后再输入正确答案：")
                right_type =input()
                right_ans = input()
                p_num =len(right_ans)
                p_xy=''
                c_xy=''
                if(right_type =='判断'):  
                    if(right_ans=='a' or right_ans =='A'):
                        p_xy='1240'
                    else:
                        p_xy='1410'
                    c_xy='1680'
                elif( right_type == '单选'):
                    if(right_ans=='a' or right_ans =='A'):
                        p_xy='1240'
                    elif(right_ans=='b' or right_ans =='B'):
                        p_xy='1410'
                    elif(right_ans=='c' or right_ans =='C'):
                        p_xy='1610'
                    else:
                        p_xy='1780'
                    c_xy='2050'
                elif(right_type == '三选'):
                    if(right_ans=='a' or right_ans =='A'):
                        p_xy='1240'
                    elif(right_ans=='b' or right_ans =='B'):
                        p_xy='1410'
                    else:
                        p_xy='1610'
                    c_xy='1870'
                else:
                    if('a' in right_ans or 'A' in right_ans):
                        p_xy='1240|'
                    if('b' in right_ans or 'B' in right_ans):
                        p_xy=p_xy+'1410|'
                    if('c' in right_ans or 'C' in right_ans):
                        p_xy=p_xy+'1610|'
                    if('d' in right_ans or 'D' in right_ans):
                        p_xy=p_xy+'1780|'
                    if('e' in right_ans or 'E' in right_ans):
                        p_xy+='1950'
                    c_xy='2280'
                insert_sql = """INSERT INTO sheet1(type,question,right_ans,right_point,point_xy,click_xy) VALUES ('%s','%s','%s',%d,'%s','%s')""" % (
                right_type,text, right_ans,p_num,p_xy,c_xy)
                print(insert_sql)
                cursor.execute(insert_sql)
                db.commit()
    # 关闭数据库连接
    cursor.close()
    db.close()
    
    if(len(row)==1):
        if(what_point_num>0):
            xylist=what_point_xy.split('|')
            for i in range(what_point_num):
                os.system('adb shell input tap 500 %s'%xylist[i])
                os.system('adb shell input tap 500 %s'%xylist[i])
                os.system('adb shell input tap 500 %s'%xylist[i])
                time.sleep(1)
            time.sleep(0.5)
            os.system('adb shell input tap 500 %s'%what_click)
            os.system('adb shell input tap 500 %s'%what_click)
            time.sleep(3)
            continue

        if(what_type_want !='多选'):
            if(what_i_want=='a'or what_i_want=='A'):
                os.system('adb shell input tap 500 1215')
                os.system('adb shell input tap 500 1215')
                os.system('adb shell input tap 500 1215')
                os.system('adb shell input swipe 500 1215 600 1230')
            elif(what_i_want=='b' or what_i_want =='B'):
                os.system('adb shell input tap 500 1415')
                os.system('adb shell input tap 500 1415')
                os.system('adb shell input tap 500 1415')
                os.system('adb shell input swipe 500 1415 600 1430')
            elif(what_i_want=='c' or what_i_want =='C'):
                os.system('adb shell input tap 500 1615')
                os.system('adb shell input tap 500 1615')
                os.system('adb shell input tap 500 1615')
                os.system('adb shell input swipe 500 1615 600 1630')
            elif(what_i_want=='d' or what_i_want =='D'):
                os.system('adb shell input tap 500 1815')
                os.system('adb shell input tap 500 1815')
                os.system('adb shell input tap 500 1815')
                os.system('adb shell input swipe 500 1815 600 1830')
        # else:
        #     if('a' in what_i_want or 'A' in what_i_want):
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #     elif('b' in what_i_want or 'B' in what_i_want):
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #     elif('c' in what_i_want or 'C' in what_i_want):
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #     elif('d' in what_i_want or 'D' in what_i_want):
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #     elif('e' in what_i_want or 'E' in what_i_want):
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
        #         os.system('adb shell input tap 500 1215')
            if(what_type_want == '判断'):
                os.system('adb shell input tap 650 1700')
                os.system('adb shell input tap 650 1700')
                os.system('adb shell input swipe 650 1700 700 1730')
            elif(what_type_want == '三选'):
                os.system('adb shell input tap 650 1900')
                os.system('adb shell input tap 650 1900')
                os.system('adb shell input swipe 650 1800 700 1900')
            else:
                os.system('adb shell input tap 650 2100')
                os.system('adb shell input tap 650 2100')
                os.system('adb shell input swipe 650 2000 700 2100')
            # os.remove("./question%d.png" % file_name)  
            old_text=text
            time.sleep(1)
            continue
    else:
        print("--手动选择--")
    # os.remove("./question%d.png" % file_name)
    print("回车继续下一题")
    aaa = input()
   
