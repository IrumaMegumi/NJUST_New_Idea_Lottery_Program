import random

main_word_dict={0:'情绪价值',1:'社交能耗',2:'信息茧房',3:'被动学习',
                4:'思维惰性',5:'唯成绩论',6:'专注力流失',7:'时间碎片化',
                8:'AI过度依赖',9:'无纸化学习',10:'产学研联合',11:'“内卷式”竞争',
                12:'自媒体创业',13:'天坑专业',14:'适应与改变',15:'教室沉默',
                16:'35岁危机',17:'创新驱动力',18:'智能教育',19:'未来产业'}

supplement_word_dict={0:'唯成绩论',1:'电影哪吒',2:'人际关系',3:'水课',
                      4:'选择大于努力',5:'AI焦虑',6:'多学科融合',7:'学历贬值',
                      8:'理论与实践',9:'中国智造'}

name=input('请输入你的姓名：')
main_index=list(main_word_dict.keys())
random.shuffle(main_index)
main_keyword=main_word_dict[main_index[0]]
supplement_index=list(supplement_word_dict.keys())
random.shuffle(supplement_index)
supplement_keyword=supplement_word_dict[supplement_index[0]]
print(f"你的第一关键词是：{main_keyword}")
print(f"你的候补关键词是：{supplement_keyword}")
