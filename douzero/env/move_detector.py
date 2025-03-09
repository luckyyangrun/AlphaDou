from douzero.env.utils import *
import collections

# 全局癞子牌数值，默认为 None；使用 set_wild_rank(wild) 设置
WILD_RANK = None

def set_wild_rank(wild):
    global WILD_RANK
    WILD_RANK = wild

def effective_rank(move):
    """
    计算动作的有效牌值：
    - 如果动作中存在非癞子牌，则返回其中最小（或首个）的自然牌值；
    - 否则返回 WILD_RANK 本身。
    """
    global WILD_RANK
    natural = [card for card in move if card != WILD_RANK]
    if natural:
        return min(natural)
    else:
        return WILD_RANK

def is_continuous_seq(move):
    # 假设 move 已排序且不含癞子牌
    for i in range(len(move) - 1):
        if move[i+1] - move[i] != 1:
            return False
    return True

def get_move_type(move):
    """
    根据动作 move 判断出牌类型，支持癞子牌使用。
    若动作中含有癞子牌（WILD_RANK），则用 effective_rank() 得到比较值。
    """
    move_size = len(move)
    move_dict = collections.Counter(move)
    
    # Pass
    if move_size == 0:
        return {'type': TYPE_0_PASS}
    
    if move_size == 1:
        return {'type': TYPE_1_SINGLE, 'rank': move[0]}
    
    if move_size == 2:
        # 对子：自然牌相同，或一自然一癞子补全
        if move[0] == move[1]:
            return {'type': TYPE_2_PAIR, 'rank': move[0]}
        elif (WILD_RANK in move) and ((move[0] != WILD_RANK) or (move[1] != WILD_RANK)):
            return {'type': TYPE_2_PAIR, 'rank': effective_rank(move)}
        elif move == [20, 30]:
            return {'type': TYPE_5_KING_BOMB}
        else:
            return {'type': TYPE_15_WRONG}
    
    if move_size == 3:
        # 三条：全部相同，或利用癞子补齐
        if len(move_dict) == 1:
            return {'type': TYPE_3_TRIPLE, 'rank': effective_rank(move)}
        else:
            for card, count in move_dict.items():
                if card != WILD_RANK and count + move_dict.get(WILD_RANK, 0) >= 3:
                    return {'type': TYPE_3_TRIPLE, 'rank': card}
            return {'type': TYPE_15_WRONG}
    
    if move_size == 4:
        if len(move_dict) == 1:
            return {'type': TYPE_4_BOMB, 'rank': effective_rank(move)}
        elif len(move_dict) == 2:
            # 可能为三带一：排序后检查前3或后3是否相同（含癞子情况）
            sorted_move = sorted(move)
            if sorted_move[0] != WILD_RANK and sorted_move[0] == sorted_move[1] == sorted_move[2]:
                return {'type': TYPE_6_3_1, 'rank': sorted_move[0]}
            elif sorted_move[-1] != WILD_RANK and sorted_move[-1] == sorted_move[-2] == sorted_move[-3]:
                return {'type': TYPE_6_3_1, 'rank': sorted_move[-1]}
            else:
                return {'type': TYPE_15_WRONG}
        else:
            return {'type': TYPE_15_WRONG}
    
    # 判断单顺（TYPE_8_SERIAL_SINGLE），支持癞子牌补全
    natural = sorted([card for card in move if card != WILD_RANK])
    wild_count = move_dict.get(WILD_RANK, 0)
    if natural:
        candidate = list(range(natural[0], natural[0] + move_size))
        missing = sum(1 for c in candidate if c not in natural)
        if missing <= wild_count:
            return {'type': TYPE_8_SERIAL_SINGLE, 'rank': natural[0], 'len': move_size}
    # 5 张牌可能为三带二
    if move_size == 5:
        if len(move_dict) == 2:
            for card, count in move_dict.items():
                if card != WILD_RANK and count + move_dict.get(WILD_RANK, 0) == 3:
                    return {'type': TYPE_7_3_2, 'rank': card}
        return {'type': TYPE_15_WRONG}
    
    # 6 牌、8 牌及序列型（连对、连三等）采用原逻辑，使用 effective_rank() 替代直接取值
    count_dict = collections.defaultdict(int)
    for c, n in move_dict.items():
        count_dict[n] += 1

    if move_size == 6:
        if (len(move_dict) in [2,3]) and count_dict.get(4) == 1 and \
           (count_dict.get(2) == 1 or count_dict.get(1) == 2):
            return {'type': TYPE_13_4_2, 'rank': effective_rank(move)}
    
    if move_size == 8 and (((len(move_dict) in [2,3]) and (count_dict.get(4) == 1 and count_dict.get(2) == 2)) \
       or count_dict.get(4) == 2):
        natural_bombs = [c for c, n in move_dict.items() if c != WILD_RANK and n == 4]
        if natural_bombs:
            return {'type': TYPE_14_4_22, 'rank': max(natural_bombs)}
    
    mdkeys = sorted([k for k in move_dict.keys() if k != WILD_RANK])
    if mdkeys and (len(move_dict) == count_dict.get(2)) and is_continuous_seq(mdkeys):
        return {'type': TYPE_9_SERIAL_PAIR, 'rank': mdkeys[0], 'len': len(mdkeys)}
    
    if mdkeys and (len(move_dict) == count_dict.get(3)) and is_continuous_seq(mdkeys):
        return {'type': TYPE_10_SERIAL_TRIPLE, 'rank': mdkeys[0], 'len': len(mdkeys)}
    
    if count_dict.get(3, 0) >= MIN_TRIPLES:
        serial_3 = []
        single = []
        pair = []
        for k, v in move_dict.items():
            if k == WILD_RANK:
                continue
            if v >= 3:
                serial_3.append(k)
            elif v == 1:
                single.append(k)
            elif v == 2:
                pair.append(k)
            else:
                return {'type': TYPE_15_WRONG}
        serial_3.sort()
        if is_continuous_seq(serial_3):
            if len(serial_3) == len(single) + len(pair)*2:
                return {'type': TYPE_11_SERIAL_3_1, 'rank': serial_3[0], 'len': len(serial_3)}
            if len(serial_3) == len(pair) and len(move_dict) == len(serial_3)*2:
                return {'type': TYPE_12_SERIAL_3_2, 'rank': serial_3[0], 'len': len(serial_3)}
        if len(serial_3) == 4:
            if is_continuous_seq(serial_3[1:]):
                return {'type': TYPE_11_SERIAL_3_1, 'rank': serial_3[1], 'len': len(serial_3)-1}
            if is_continuous_seq(serial_3[:-1]):
                return {'type': TYPE_11_SERIAL_3_1, 'rank': serial_3[0], 'len': len(serial_3)-1}
    
    return {'type': TYPE_15_WRONG}

