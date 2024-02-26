S: str = ''  # 文法开始符
production: dict = {}   # 产生式集合
production_set: list = []      # 产生式集合
vn: list = []    # 非终结符集合
vt: list = []    # 终结符集合
From: str = ''      # 分析方法
FHash: dict = {'LL(1)分析法': 'LL(1)', 'LR(0)分析法': 'LR(0)',
               'SLR(1)分析法': 'SLR(1)', 'LR(1)分析法': 'LR(1)', 'LALR(1)分析法': 'LALR(1)'}

First: dict = {}    # First集合
Follow: dict = {}   # Follow集合
Select: dict = {}   # Select集合
Closure_LR0: dict = {}     # 在非终结符前加入点号
Closure_LR1: dict = {}     # 在非终结符前加入点号
Closure_SLR: dict = {}     # 在非终结符前加入点号
table_LL1: dict = {}    # LL(1)预测分析表
table_LR0: dict = {}    # LR(0)预测分析表
table_SLR: dict = {}    # SLR预测分析表
table_LR1: dict = {}    # LR(1)预测分析表
table_LALR: dict = {}   # LALR(1)预测分析表
status_LR0: list = []   # 记录状态的编号
status_SLR: list = []   # 记录状态的编号
status_LR1: list = []   # 记录状态的编号
same: list = []    # 记录同一集合


def init(sel: str):
    global S, From
    S = ''
    From = sel  # 分析方法
    production.clear()
    production_set.clear()
    vn.clear()
    vt.clear()

    First.clear()
    Follow.clear()
    Select.clear()
    Closure_LR0.clear()
    Closure_LR1.clear()
    Closure_SLR.clear()
    table_LL1.clear()
    table_LR0.clear()
    table_SLR.clear()
    table_LR1.clear()
    table_LALR.clear()
    status_LR0.clear()
    status_SLR.clear()
    status_LR1.clear()
    same.clear()


def read(gram: str):    # 读取文法
    global S
    strlen = len(gram)
    left: str = ''  # 产生式左部
    right: str = ''  # 产生式右部
    flag: bool = True
    for i in range(strlen):
        if S == '':     # 文法开始符
            S = gram[i]

        if (i == (strlen - 1)) or (gram[i] == '\n'):  # 换行
            if i == (strlen - 1):
                if left not in production.keys():
                    production[left] = []
                production[left].append(right + gram[i])  # 获得产生式 left->right + Gram[i]
                # print(left, right + Gram[i])
            else:
                if left not in production.keys():
                    production[left] = []
                production[left].append(right)     # 获得产生式 left->right
                # print(left, right)
            right = ''     # 清空right
            flag = True     # 换行重置flag
            continue

        if flag:    # 还未读取left
            left = gram[i]
            flag = False    # 已经读取left
        else:
            if (gram[i] == '-') or (gram[i] == '>'):    # 读到箭头continue
                continue

            if gram[i] == '|':
                if left not in production.keys():
                    production[left] = []
                production[left].append(right)  # 获得left->right
                # print(left, right)
                right = ''
            else:
                right = right + gram[i]     # 添加到当前的right

    for left in production.keys():      # 全部非终结符的集合
        if left not in vn:
            vn.append(left)

    for rights in production.values():       # 全部终结符的集合
        for right in rights:
            for ch in right:
                if (ch not in vt) and (ch not in vn) and (ch != '~'):
                    vt.append(ch)

    for left in production.keys():
        for right in production[left]:
            production_set.append(left + '->' + right)

    # print('production_set:', production_set)
    # print('vn:', vn)
    # print('vt:', vt)


def trans_table(list1, list2, table: dict):   # 将table转换成字符串
    res: str = '\t\t'
    for ch in list2:
        res = res + str(ch) + '\t\t'
    res = res + '\n'

    for han in list1:
        res = res + str(han) + '\t\t'
        for lie in list2:
            if (str(han), str(lie)) in table.keys():
                res = res + table[(str(han), str(lie))] + '\t\t'
            else:
                res = res + '\t\t'
        res = res + '\n'
    res = FHash[From] + '预测分析表:' + '\n' + res
    # print(res)
    return res


def get_empty(left: str):
    # 判断是否可以推空，True为可以推空
    flag: bool = False
    for right in production[left]:  # 遍历left的右部集合
        res: bool = True
        for ch in right:    # 遍历右部每个字符
            if ch in vn:    # 如果是非终结符
                if (ch != left) and (not get_empty(ch)):    # 如果不可推空
                    res = False     # res推空失败
                    break
            else:   # 如果是终结符
                if ch != '~':   # 如果不是空字
                    res = False
                    break

        flag = flag or res  # 该右部可以推空，进行or操作

    return flag     # 放回flag


def find_first(left: str):
    if left in First.keys():   # 如果left的First集合已经找到则直接退出
        return
    First[left] = set()     # 先放一个空集合
    for right in production[left]:
        for ch in right:
            if ch in vn:    # 如果是非终结符
                if ch not in First.keys():  # 如果该非终结符的First没有找到
                    find_first(ch)
                First[left].update(First[ch])   # 将ch的First假如left的First集合

                if not get_empty(ch):   # 如果ch不能推空则退出
                    break
            else:   # 如果是终结符
                First[left].add(ch)     # 将ch加入left的First集
                break

    First[left].discard('~')
    if get_empty(left):     # 如果可以推空
        First[left].add('~')    # 将空字加入First


def get_first():
    for left in production.keys():  # 找到所有的left的First集合
        find_first(left)
    # print('First:', First)


def find_follow1(ch: str):  # 用规则1求解ch的Follow集合
    Follow[ch] = set()
    if ch == S:  # 如果是文法开始符
        Follow[ch].add('#')  # Follow集加入#号
    for rights in production.values():
        for right in rights:    # 遍历所有右部集合
            for i in range(len(right)):
                if right[i] == ch:  # vn出现在该右部
                    if i == len(right) - 1:
                        Follow[ch].add('#')     # 位于最后一个字符
                    else:
                        for j in range(i + 1, len(right)):  # 遍历后面的字符
                            if right[j] in vn:  # 如果是非终结符，将first集加入follow集合中
                                tmp = set()
                                tmp.update(First[right[j]])
                                tmp.discard('~')    # 去掉空
                                Follow[ch].update(tmp)
                                if get_empty(right[j]):  # 如果可以推空
                                    if j == len(right) - 1:  # 最后一个字符都可以推空
                                        Follow[ch].add('#')  # 加入#
                                else:
                                    break   # 退出
                            else:   # 如果是终结符
                                Follow[ch].add(right[j])
                                break


def find_follow2(ch: str):  # 用规则2求解完整的Follow集
    for left in production.keys():
        for right in production[left]:  # 遍历所有右部
            for i in range(len(right)):
                if ch == right[i]:
                    if i == len(right) - 1:  # 如果位于末尾
                        Follow[ch].update(Follow[left])  # 将Follow加入
                    else:
                        for j in range(i + 1, len(right)):  # 遍历后面的字符
                            if right[j] in vn:  # 如果是非终结符
                                if get_empty(right[j]):  # 如果可以推空
                                    if j == len(right) - 1:  # 如果推到末尾
                                        Follow[ch].update(Follow[left])  # 将Follow加入
                                else:
                                    break
                            else:
                                break


def get_follow():   # 求解完整的Follow集
    for left in production.keys():  # 执行规则1
        find_follow1(left)

    old_sz: int = 0     # old统计全部Follow集合的大小
    for follow in Follow.values():
        old_sz = old_sz + len(follow)

    for left in production.keys():  # 执行规则2
        find_follow2(left)

    new_sz: int = 0
    for follow in Follow.values():  # new统计全部Follow集合的大小
        new_sz = new_sz + len(follow)

    while old_sz != new_sz:     # 反复执行，直到follow集合不再扩大
        for left in production.keys():
            find_follow2(left)
        old_sz = new_sz  # new值变成old值
        new_sz = 0
        for follow in Follow.values():  # new计算新的Follow集合的大小
            new_sz = new_sz + len(follow)

    # print('Follow:', Follow)


def get_select():
    for left in production.keys():
        for right in production[left]:
            Select[(left, right)] = set()
            for i in range(len(right)):  # 求 left -> right 的 select 集合
                if right[i] in vn:  # 如果是非终结符
                    tmp = set()
                    tmp.update(First[right[i]])
                    tmp.discard('~')    # 去掉空字符
                    Select[(left, right)].update(tmp)   # first集加入到Select中
                    if get_empty(right[i]):     # 如果该字符可以推空
                        if i == len(right) - 1:     # 如果最后一个字符都可以推空
                            # 将左部的Follow加入到Select中
                            Select[(left, right)].update(Follow[left])
                    else:   # 如果不可以推空
                        break
                else:   # 如果是终结符
                    if right[i] == '~':
                        # 将左部的Follow加入到Select中
                        Select[(left, right)].update(Follow[left])
                    else:
                        Select[(left, right)].add(right[i])
                    break
    # print('Select:', Select)


def get_table_ll1():
    for formulas in Select.keys():
        for ch in Select[formulas]:
            table_LL1[(formulas[0], ch)] = formulas[1]
    # print('table_LL1:', table_LL1)


def after_point(pro: str):  # 返回'.'后的字符
    for i in range(len(pro) - 1):
        if pro[i] == '.':
            return pro[i + 1]
    return '~'


def after_point_2(pro: str):
    for i in range(len(pro) - 2):
        if pro[i] == '.':
            return pro[i + 2]
    return '~'


def move_point(pro: str):
    for i in range(len(pro) - 1):
        if pro[i] == '.':
            res = pro[0:i] + pro[i + 1] + pro[i] + pro[i + 2:len(pro)]
            return res
    return pro


def get_idx(pro1: str):     # 求产生式的编号
    cot: int = 1
    for pro2 in production_set:
        if pro2 + '.' == pro1:
            return cot
        cot = cot + 1
    return 0


def get_pro(idx: int):
    return production_set[idx - 1]

# ---------------------------LR0----------------------------------


def find_closure_lr0():    # 在非终结符前加入点号
    old = -1
    new = 0
    for left in production.keys():
        Closure_LR0[left] = set()
    while old != new:
        for left in production.keys():
            for right in production[left]:
                Closure_LR0[left].add(left + '->.' + right)
                if right[0] in vn:
                    Closure_LR0[left].update(Closure_LR0[right[0]])
        old = new
        new = 0
        for left in Closure_LR0.keys():
            new = new + len(Closure_LR0[left])
    # print('Closure_LR0', Closure_LR0)


def move_status_lr0(status: set, ch):    # 将状态的点号按ch字符向后移动
    res = set()
    for pro in status:
        if after_point(pro) == ch:  # 如果点号后面的字符是ch
            # 我们先将其后移放入新状态中
            new_str: str = move_point(pro)
            res.add(new_str)
            new_ch = after_point(new_str)
            if new_ch in vn:    # 如果新串后面是非终结符
                # 将其所有产生式加入新状态中
                res.update(Closure_LR0[new_ch])
    return res


def judge_end_lr0(status: set):  # 判断是否是规约项目
    for pro in status:
        if pro[len(pro) - 1] == '.':
            return True
    return False


def find_end_lr0(status: set):  # 找出规约产生式
    for pro in status:
        if pro[len(pro) - 1] == '.':
            return pro
    return ''


def get_status_idx_lr0(status: set):
    cot: int = 0
    for sta in status_LR0:
        if sta == status:
            return cot
        cot = cot + 1
    return 0


def crate_start_lr0():
    res: set = set()
    res.add(S + '\'->.' + S)
    for pro in Closure_LR0[S]:
        res.add(pro)
    return res


def crate_dfa_lr0(idx: str, status: set):   # 状态的标号，和该状态的规范族
    # print('状态号: I', idx)
    # for pro in status:
    #     print(pro)

    if idx == '0':
        status_LR0.append(status)

    flag = True
    if judge_end_lr0(status):
        flag = False
        tmp: str = str(get_idx(find_end_lr0(status)))
        if tmp == '0':  # S'->S.
            table_LR0[(idx, '#')] = 'acc'
        else:
            for ch in vt:
                table_LR0[(idx, ch)] = 'r' + tmp
            table_LR0[(idx, '#')] = 'r' + tmp

    all_after = set()
    for pro in status:
        if after_point(pro) != '~':
            all_after.add(after_point(pro))

    for ch in all_after:    # 当于连ch边到状态new_status
        new_status = move_status_lr0(status, ch)
        if new_status not in status_LR0:
            status_LR0.append(new_status)
            crate_dfa_lr0(str(len(status_LR0) - 1), new_status)

        # idx  -- ch --> status_index[new_status]
        tmp: str = str(get_status_idx_lr0(new_status))
        if ch in vt:
            if flag:
                table_LR0[(idx, ch)] = 's' + tmp
        else:
            table_LR0[(idx, ch)] = tmp


# ---------------------------SLR----------------------------------

def find_closure_slr():    # 在非终结符前加入点号
    old = -1
    new = 0
    for left in production.keys():
        Closure_SLR[left] = set()
    while old != new:
        for left in production.keys():
            for right in production[left]:
                Closure_SLR[left].add(left + '->.' + right)
                if right[0] in vn:
                    Closure_SLR[left].update(Closure_SLR[right[0]])
        old = new
        new = 0
        for left in Closure_SLR.keys():
            new = new + len(Closure_SLR[left])
    # print('Closure_SLR', Closure_SLR)


def move_status_slr(status: set, ch):    # 将状态的点号按ch字符向后移动
    res = set()
    for pro in status:
        if after_point(pro) == ch:  # 如果点号后面的字符是ch
            # 我们先将其后移放入新状态中
            new_str: str = move_point(pro)
            res.add(new_str)
            new_ch = after_point(new_str)
            if new_ch in vn:    # 如果新串后面是非终结符
                # 将其所有产生式加入新状态中
                res.update(Closure_SLR[new_ch])
    return res


def judge_end_slr(status: set):  # 判断是否是规约项目
    for pro in status:
        if pro[len(pro) - 1] == '.':
            return True
    return False


def find_end_slr(status: set):  # 找出规约产生式
    for pro in status:
        if pro[len(pro) - 1] == '.':
            return pro
    return ''


def get_status_idx_slr(status: set):
    cot: int = 0
    for sta in status_SLR:
        if sta == status:
            return cot
        cot = cot + 1
    return 0


def crate_start_slr():
    res: set = set()
    res.add(S + '\'->.' + S)
    for pro in Closure_SLR[S]:
        res.add(pro)
    return res


def crate_dfa_slr(idx: str, status: set):   # 状态的标号，和该状态的规范族
    # print('状态号: I', idx)
    # for pro in status:
    #     print(pro)

    if idx == '0':
        status_SLR.append(status)

    if judge_end_slr(status):
        pro: str = find_end_slr(status)
        tmp: str = str(get_idx(pro))
        if tmp == '0':  # S'->S.
            table_SLR[(idx, '#')] = 'acc'
        else:
            for ch in Follow[pro[0]]:
                table_SLR[(idx, ch)] = 'r' + tmp

    all_after = set()
    for pro in status:
        if after_point(pro) != '~':
            all_after.add(after_point(pro))

    for ch in all_after:    # 当于连ch边到状态new_status
        new_status = move_status_slr(status, ch)
        if new_status not in status_SLR:
            status_SLR.append(new_status)
            crate_dfa_slr(str(len(status_SLR) - 1), new_status)

        # idx  -- ch --> status_index[new_status]
        tmp: str = str(get_status_idx_slr(new_status))
        if ch in vt:
            table_SLR[(idx, ch)] = 's' + tmp
        else:
            table_SLR[(idx, ch)] = tmp

# ---------------------------LR(1)----------------------------------


def get_closure_lr1(pro: str, ch: str):
    temp_first = set()
    ch1 = after_point(pro)  # S -> a.ch1ch2, ch
    ch2 = after_point_2(pro)

    if ch2 == '~':
        temp_first.add(ch)
    elif ch2 in vt:
        temp_first.add(ch2)
    else:
        temp_first.update(First[ch2])
    if '~' in temp_first:
        temp_first.remove('~')
        temp_first.add(ch)

    res: set = set()
    for right in production[ch1]:
        for ch3 in temp_first:
            temp: str = ch1 + "->." + right
            res.add((temp, ch3))

    return res


def find_closure_lr1(pro, ch):
    res: set = set()
    res.add((pro, ch))
    old = -1
    new = len(res)
    while old != new:
        temp: set = set()
        for pro in res:
            if after_point(pro[0]) in vn:
                temp.update(get_closure_lr1(pro[0], pro[1]))
        res.update(temp)
        old = new
        new = len(res)
    return res


def move_status_lr1(status: set, ch: str):
    res = set()
    for pro in status:
        if after_point(pro[0]) == ch:  # 如果点号后面的字符是ch
            # 我们先将其后移放入新状态中
            new_str: str = move_point(pro[0])
            res.add((new_str, pro[1]))
            new_ch = after_point(new_str)
            if new_ch in vn:  # 如果新串后面是非终结符
                res.update(find_closure_lr1(new_str, pro[1]))
    return res


def judge_end_lr1(status: set):  # 判断是否是规约项目
    for pro in status:
        if pro[0][len(pro[0]) - 1] == '.':
            return True
    return False


def find_end_lr1(status: set):  # 找出规约产生式
    for pro in status:
        if pro[0][len(pro[0]) - 1] == '.':
            return pro[0]
    return ''


def get_status_idx_lr1(status: set):
    cot: int = 0
    for sta in status_LR1:
        if sta == status:
            return cot
        cot = cot + 1
    return 0


def crate_dfa_lr1(idx: str, status: set):
    # print('状态号: I', idx)
    # for pro in status:
    #     print(pro)

    if idx == '0':
        status_LR1.append(status)

    if judge_end_lr1(status):
        pro: str = find_end_lr1(status)
        tmp: str = str(get_idx(pro))
        if tmp == '0':  # S'->S.
            table_LR1[(idx, '#')] = 'acc'
        else:
            for pro2 in status:
                if pro2[0] == pro:
                    table_LR1[(idx, pro2[1])] = 'r' + tmp

    all_after = set()
    for pro in status:
        if after_point(pro[0]) != '~':
            all_after.add(after_point(pro[0]))

    for ch in all_after:    # 当于连ch边到状态new_status
        new_status = move_status_lr1(status, ch)
        if new_status not in status_LR1:
            status_LR1.append(new_status)
            crate_dfa_lr1(str(len(status_LR1) - 1), new_status)
        # idx  -- ch --> status_index[new_status]
        tmp: str = str(get_status_idx_lr1(new_status))
        if ch in vt:
            table_LR1[(idx, ch)] = 's' + tmp
        else:
            table_LR1[(idx, ch)] = tmp


def crate_start_lr1():
    res: set = set()
    res.update(find_closure_lr1(S + "'->." + S, '#'))
    return res

# ---------------------------LALR(1)----------------------------------


def judge_same(s1: set, s2: set):
    t1: set = set()
    t2: set = set()
    for t in s1:
        t1.add(t[0])
    for t in s2:
        t2.add(t[0])

    if t1 == t2:
        return True
    else:
        return False


def union(s1: str, s2: str):
    res = ''
    if (s1[0] == 's') or (s1[0] == 'r'):
        res = res + s1[0]
    l1: list = []
    for ch in s1:
        if (ch != 's') and (ch != 'r'):
            if ch not in l1:
                l1.append(ch)
    for ch in s2:
        if (ch != 's') and (ch != 'r'):
            if ch not in l1:
                l1.append(ch)
    l1.sort()
    res = res + ''.join(l1)
    return res


def crate_table_lalr():
    vis = []
    tongyi = []
    for i in range(len(status_LR1)):
        vis.append(0)
        tongyi.append([str(i)])

    for i in range(len(status_LR1)):
        if vis[i] != 0:
            continue
        for j in range(i + 1, len(status_LR1)):
            if judge_same(status_LR1[i], status_LR1[j]):
                vis[j] = i
                tongyi[i] = tongyi[i] + tongyi[j]

    dic: dict = {}
    for i in range(len(status_LR1)):
        if vis[i] == 0:
            dic[str(i)] = ''.join(tongyi[i])
        else:
            dic[str(i)] = ''.join(tongyi[vis[i]])

    for i in range(len(status_LR1)):
        for ch in vt + ['#']:
            if ((str(i), ch) in table_LR1.keys()) and (table_LR1[(str(i), ch)][0] == 's'):
                table_LR1[(str(i), ch)] = table_LR1[(str(i), ch)][0] + dic[table_LR1[(str(i), ch)][1:]]
        for ch in vn:
            if (str(i), ch) in table_LR1.keys():
                table_LR1[(str(i), ch)] = dic[table_LR1[(str(i), ch)]]

    for i in range(len(status_LR1)):
        if vis[i] != 0:
            continue
        now = ''.join(tongyi[i])
        same.append(now)
        for j in tongyi[i]:
            for ch in vt + ['#'] + vn:
                if (j, ch) in table_LR1.keys():
                    table_LALR[(now, ch)] = table_LR1[(j, ch)]

# ---------------------------analyse----------------------------------


def get_stack(list1: list):
    res: str = ''
    for ch in list1:
        res = res + str(ch)
    return res


def get_remain(pt, sentence):
    res: str = ''
    for i in range(pt, len(sentence)):
        res = res + sentence[i]
    return res


def analyse_ll(sentence: str):
    sentence_len: int = max(len(sentence) + int(len(sentence) / 2), 16)
    sentence = sentence + '#'
    res: str = '步骤'.ljust(sentence_len - 2) + '分析栈'.ljust(sentence_len - 3) + '当前输入'.ljust(sentence_len - 4)
    res = res + '剩余输入串'.ljust(sentence_len - 5) + '所用产生式' + '\n'

    sta = ['#', S]    # 分析栈
    step = 0    # 步骤数
    pt = 0  # 指向输入串的指针
    while True:
        a = sentence[pt]    # 指针指向的字符
        x = sta[len(sta) - 1]   # 栈顶字符
        if x == '#':    # 如果栈顶是#
            if x == a:
                step = step + 1
                res = res + str(step).ljust(sentence_len) + get_stack(sta).ljust(sentence_len)
                res = res + sentence[pt].ljust(sentence_len) + get_remain(pt, sentence).ljust(sentence_len)
                res = res + '分析成功' + '\n'
            else:
                res = res + '分析失败' + '\n'
            return res
        elif x in vt:
            if x == a:
                step = step + 1
                res = res + str(step).ljust(sentence_len) + get_stack(sta).ljust(sentence_len)
                res = res + sentence[pt].ljust(sentence_len) + get_remain(pt, sentence).ljust(sentence_len)
                res = res + '\n'
                sta.pop()
                pt = pt + 1
            else:
                res = res + '分析失败' + '\n'
        else:   # 如果栈顶元素是非终结符，则查看预测分析表是否有表达式，如果有则倒序加入栈中
            if (x, a) in table_LL1.keys():
                tmp = table_LL1[(x, a)]
                step = step + 1
                res = res + str(step).ljust(sentence_len) + get_stack(sta).ljust(sentence_len)
                res = res + sentence[pt].ljust(sentence_len) + get_remain(pt, sentence).ljust(sentence_len)
                res = res + tmp + '\n'
                sta.pop()
                for i in range(len(tmp)):
                    if tmp[len(tmp) - i - 1] != '~':
                        sta.append(tmp[len(tmp) - i - 1])
            else:
                res = res + '分析失败' + '\n'
                return res


def analyse_lr(sentence: str, table: dict):
    sentence_len: int = max(len(sentence) + int(len(sentence) / 2), 16)
    sentence = sentence + '#'
    res: str = '步骤'.ljust(sentence_len - 2) + '状态栈'.ljust(sentence_len - 3) + '符号栈'.ljust(
        sentence_len - 3) + '输入串'.ljust(sentence_len - 3) + '操作说明' + '\n'
    status = []  # 分析栈
    symbol = []  # 符号栈
    status.append('0')
    symbol.append('#')
    pt = 0
    step = 0
    while True:
        if (status[len(status) - 1], sentence[pt]) in table.keys():
            step = step + 1
            res = res + str(step).ljust(sentence_len) + get_stack(status).ljust(sentence_len)
            res = res + get_stack(symbol).ljust(sentence_len) + get_remain(pt, sentence).ljust(sentence_len)
            if table[(status[len(status) - 1], sentence[pt])] == 'acc':
                res = res + '分析成功' + '\n'
                return res
            if table[(status[len(status) - 1], sentence[pt])][0] == 's':
                res = res + 'ACTION[' + status[len(status) - 1] + ',' + sentence[pt] + ']='
                res = res + table[(status[len(status) - 1], sentence[pt])] + '\n'
                status.append(table[(status[len(status) - 1], sentence[pt])][1:])
                symbol.append(sentence[pt])
                pt = pt + 1
            else:
                res = res + table[(status[len(status) - 1], sentence[pt])] + ': '
                res = res + get_pro(int(table[(status[len(status) - 1], sentence[pt])][1:]))
                temp = get_pro(int(table[(status[len(status) - 1], sentence[pt])][1:]))
                left = temp[0]
                right = temp[3: len(temp)]
                for i in range(len(right)):
                    j = len(right) - i - 1
                    if symbol[len(symbol) - 1] != right[j]:
                        res = res + '分析失败' + '\n'
                        return res
                    symbol.pop()
                    status.pop()
                symbol.append(left)
                if (status[len(status) - 1], symbol[len(symbol) - 1]) not in table.keys():
                    res = res + '分析失败' + '\n'
                    return res
                res = res + ', GOTO(' + str(status[len(status) - 1]) + ',' + symbol[len(symbol) - 1]
                res = res + ')=' + table[(status[len(status) - 1], symbol[len(symbol) - 1])] + '\n'
                status.append(table[(status[len(status) - 1], symbol[len(symbol) - 1])])
        else:
            res = res + '分析失败' + '\n'
            return res


def create_table(gram: str, sel: str):
    init(sel)
    read(gram)  # 对文法进行分析
    get_first()  # 求First集合
    get_follow()  # 求Follow集合
    if From == 'LL(1)分析法':
        get_select()    # 求Select集合
        get_table_ll1()     # 求LL(1)预测分析表
        return trans_table(vn, vt + ['#'], table_LL1)
    else:
        if From == 'LR(0)分析法':
            find_closure_lr0()     # 在非终结符前加入点号
            crate_dfa_lr0('0', crate_start_lr0())
            return trans_table(list(range(len(status_LR0))), vt + ['#'] + vn, table_LR0)
        elif From == 'SLR(1)分析法':
            find_closure_slr()
            crate_dfa_slr('0', crate_start_slr())
            return trans_table(list(range(len(status_SLR))), vt + ['#'] + vn, table_SLR)
        elif From == 'LR(1)分析法':
            crate_dfa_lr1('0', crate_start_lr1())
            return trans_table(list(range(len(status_LR1))), vt + ['#'] + vn, table_LR1)
        else:
            crate_dfa_lr1('0', crate_start_lr1())
            crate_table_lalr()
            return trans_table(same, vt + ['#'] + vn, table_LALR)


def analysis(sentence: str):
    if From == 'LL(1)分析法':
        return analyse_ll(sentence)
    else:
        if From == 'LR(0)分析法':
            return analyse_lr(sentence, table_LR0)
        elif From == 'SLR(1)分析法':
            return analyse_lr(sentence, table_SLR)
        elif From == 'LR(1)分析法':
            return analyse_lr(sentence, table_LR1)
        else:
            return analyse_lr(sentence, table_LALR)
