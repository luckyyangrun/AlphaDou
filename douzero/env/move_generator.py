from douzero.env.utils import MIN_SINGLE_CARDS, MIN_PAIRS, MIN_TRIPLES, select
import collections
import itertools

class MovesGener(object):
    """
    用于生成斗地主出牌组合，支持单癞子玩法。
    当 wild_rank 不为 None 时，表示启用癞子模式，此时手牌中等于 wild_rank 的牌
    被视为癞子牌，在生成牌型时若需要补全，则会显式以 wild_rank 形式出现在组合中，
    而不是用目标牌的点数替代。
    """
    def __init__(self, cards_list, wild_rank=None):
        """
        初始化：
          - 如果传入 wild_rank，则将手牌中等于 wild_rank 的牌视为癞子牌，
            并将其他牌作为真实牌保存；同时统计癞子牌数量。
          - 如果 wild_rank 为 None，则认为没有启用癞子玩法。
          
        :param cards_list: 手牌列表（每张牌用整数表示）。
        :param wild_rank: 癞子牌点数（非大小王），启用癞子玩法时传入；否则传 None。
        """
        self.wild_rank = wild_rank
        if wild_rank is not None:
            # 分离真实牌与癞子牌：真实牌是不等于 wild_rank 的牌
            self.real_cards_list = [card for card in cards_list if card != wild_rank]
            # 癞子牌数量即手牌中等于 wild_rank 的数量
            self.wild_count = cards_list.count(wild_rank)
        else:
            self.real_cards_list = cards_list[:]
            self.wild_count = 0

        # 构造真实牌计数字典：用于判断某个牌出现了多少次
        self.cards_dict = collections.defaultdict(int)
        for card in self.real_cards_list:
            self.cards_dict[card] += 1

        # 生成各类牌型（由真实牌生成，不直接包含癞子牌，癞子牌的补全在各函数中处理）
        self.single_card_moves = []
        self.gen_type_1_single()
        self.pair_moves = []
        self.gen_type_2_pair()
        self.triple_cards_moves = []
        self.gen_type_3_triple()
        self.bomb_moves = []
        self.gen_type_4_bomb()
        self.final_bomb_moves = []
        self.gen_type_5_king_bomb()

    def _gen_serial_moves(self, cards, min_serial, repeat=1, repeat_num=0):
        """
        辅助函数：基于传入的 cards（自然牌）生成所有连续序列组合（不含癞子补全部分）。
        参数：
          - cards: 待生成序列的牌列表（一般为真实牌）。
          - min_serial: 连续序列的最小长度（例如单顺至少5张）。
          - repeat: 每个牌重复的次数（如连对需要2次，连三需要3次）。
          - repeat_num: 若大于0，则仅生成长度为 repeat_num 的序列；否则生成所有长度>=min_serial的序列。
        返回：
          - moves: 生成的连续序列组合列表，每个序列为一个排序后的列表。
        """
        if repeat_num < min_serial:
            repeat_num = 0

        single_cards = sorted(list(set(cards)))
        seq_records = []  # 记录连续子序列的起始索引和长度
        moves = []

        start = i = 0
        longest = 1
        while i < len(single_cards):
            if i + 1 < len(single_cards) and single_cards[i + 1] - single_cards[i] == 1:
                longest += 1
                i += 1
            else:
                seq_records.append((start, longest))
                i += 1
                start = i
                longest = 1

        for seq in seq_records:
            if seq[1] < min_serial:
                continue
            start, longest = seq
            longest_list = single_cards[start: start + longest]
            if repeat_num == 0:
                steps = min_serial
                while steps <= longest:
                    index = 0
                    while steps + index <= longest:
                        target_moves = sorted(longest_list[index: index + steps] * repeat)
                        moves.append(target_moves)
                        index += 1
                    steps += 1
            else:
                if longest < repeat_num:
                    continue
                index = 0
                while index + repeat_num <= longest:
                    target_moves = sorted(longest_list[index: index + repeat_num] * repeat)
                    moves.append(target_moves)
                    index += 1
        return moves

    def gen_type_1_single(self):
        """
        生成单牌动作：
          - 对于每个自然牌生成 [牌]；
          - 如果有癞子牌，则额外生成 [wild_rank]，表示单独出癞子牌。
        """
        self.single_card_moves = []
        for card in set(self.real_cards_list):
            self.single_card_moves.append([card])
        if self.wild_count > 0:
            self.single_card_moves.append([self.wild_rank])
        return self.single_card_moves

    def gen_type_2_pair(self):
        """
        生成对子动作：
          - 如果某个自然牌出现至少2次，则生成 [牌, 牌]；
          - 如果某个自然牌只出现1次，而癞子牌数量足够，则生成 [牌, wild_rank]，
            明确显示利用癞子牌补全对子。
        """
        self.pair_moves = []
        for r, count in self.cards_dict.items():
            if count >= 2:
                self.pair_moves.append([r, r])
            elif count == 1 and self.wild_count >= 1:
                self.pair_moves.append([r, self.wild_rank])
        return self.pair_moves

    def gen_type_3_triple(self):
        """
        生成三条动作：
          - 如果自然牌出现 >= 3 次，则生成 [牌, 牌, 牌]；
          - 如果出现 2 次且癞子牌足够，则生成 [牌, 牌, wild_rank]；
          - 如果出现 1 次且癞子牌足够，则生成 [牌, wild_rank, wild_rank]。
        """
        self.triple_cards_moves = []
        for r, count in self.cards_dict.items():
            if count >= 3:
                self.triple_cards_moves.append([r, r, r])
            elif count == 2 and self.wild_count >= 1:
                self.triple_cards_moves.append([r, r, self.wild_rank])
            elif count == 1 and self.wild_count >= 2:
                self.triple_cards_moves.append([r, self.wild_rank, self.wild_rank])
        return self.triple_cards_moves

    def gen_type_4_bomb(self):
        """
        生成炸弹动作：
          - 若不启用癞子模式，仅生成自然牌数量为4的炸弹 [牌,牌,牌,牌]；
          - 若启用癞子模式，对于每个自然牌 r，若其出现次数加上癞子牌数量可组成 4～12 张炸弹，
            则枚举所有可能组合，格式为 [r]*n + [wild_rank]*m，要求 n>=1。
        """
        self.bomb_moves = []
        if self.wild_rank is None:
            for r, count in self.cards_dict.items():
                if count == 4:
                    self.bomb_moves.append([r, r, r, r])
        else:
            for r, count in self.cards_dict.items():
                max_bomb_size = min(count + self.wild_count, 12)
                for size in range(4, max_bomb_size + 1):
                    wild_needed = size - count
                    if wild_needed <= self.wild_count and count > 0:
                        self.bomb_moves.append([r] * count + [self.wild_rank] * wild_needed)
        return self.bomb_moves

    def gen_type_5_king_bomb(self):
        """
        生成王炸动作：[20, 30]，不受癞子模式影响。
        """
        self.final_bomb_moves = []
        if 20 in self.real_cards_list and 30 in self.real_cards_list:
            self.final_bomb_moves.append([20, 30])
        return self.final_bomb_moves

    def gen_type_6_3_1(self):
        """
        生成“三带一”动作：
          - 从单牌动作和三条动作中选取组合，要求两部分的代表牌（即非癞子牌）不同，
            且组合中癞子牌的使用总数不超过手牌中癞子牌的数量（self.wild_count）。
          - 返回的组合格式为 [单牌] + [三条]。
        """
        result = []
        for t in self.single_card_moves:
            for i in self.triple_cards_moves:
                # 要求两部分代表牌不同
                if t[0] != i[0]:
                    # 计算该组合中使用了多少个癞子牌
                    wild_used = t.count(self.wild_rank) + i.count(self.wild_rank)
                    if wild_used <= self.wild_count:
                        result.append(t + i)
        return result

    def gen_type_7_3_2(self):
        """
        生成“三带二”动作：
          - 从对子动作和三条动作中选取组合，要求两部分代表牌不同，
            且组合中癞子牌的使用总数不超过手牌中癞子牌数量。
          - 返回的组合格式为 [对子] + [三条]。
        """
        result = []
        for t in self.pair_moves:
            for i in self.triple_cards_moves:
                if t[0] != i[0]:
                    wild_used = t.count(self.wild_rank) + i.count(self.wild_rank)
                    if wild_used <= self.wild_count:
                        result.append(t + i)
        return result

    def gen_serial_single_with_wild(self):
        """
        针对单顺（连续单牌）的补全：
          - 遍历允许的连续牌点序列（一般为 3～A，即 3～14），对于每个长度 >= MIN_SINGLE_CARDS 的序列，
          - 计算该序列中缺失的牌点个数（即该序列中哪些牌点不在真实牌中）。
          - 如果缺失的数量大于 0 且不超过 self.wild_count，则利用癞子牌补全，
            对应缺失位置用 wild_rank 表示，生成动作例如 [3, wild_rank, 5, 6, 7]。
        """
        moves = []
        allowed = list(range(3, 15))
        natural_set = set(self.real_cards_list)
        for length in range(MIN_SINGLE_CARDS, len(allowed) + 1):
            for i in range(0, len(allowed) - length + 1):
                seq = allowed[i:i+length]
                missing = sum(1 for r in seq if r not in natural_set)
                if 0 < missing <= self.wild_count:
                    move = [r if r in natural_set else self.wild_rank for r in seq]
                    moves.append(move)
        return moves

    def gen_type_8_serial_single(self, repeat_num=0):
        """
        生成单顺（连续单牌）动作：
          - 首先调用 _gen_serial_moves() 基于真实牌生成自然顺子组合；
          - 如果存在癞子牌，则调用 gen_serial_single_with_wild() 补全缺失的部分，
          - 将两部分结果合并返回。
        """
        moves = self._gen_serial_moves(self.real_cards_list, MIN_SINGLE_CARDS, repeat=1, repeat_num=repeat_num)
        if self.wild_count > 0:
            moves += self.gen_serial_single_with_wild()
        return moves

    def gen_serial_pair_with_wild(self):
        """
        生成连对动作（连续对子）的补全：
          - 遍历允许的连续牌点序列，对于每个目标对子序列，
          - 如果真实牌中某个牌点不足两张，则用 wild_rank 明确补全，
          - 例如目标 [7,7]，若只有一个 7，则输出 [7, wild_rank]。
        """
        moves = []
        allowed = list(range(3, 15))
        for length in range(MIN_PAIRS, len(allowed) + 1):
            for i in range(0, len(allowed) - length + 1):
                seq = allowed[i:i+length]
                valid = True
                missing = 0
                for r in seq:
                    count = self.cards_dict.get(r, 0)
                    if count >= 2:
                        continue
                    elif count == 1:
                        missing += 1
                    else:
                        missing += 2
                if missing > 0 and missing <= self.wild_count:
                    move = []
                    for r in seq:
                        count = self.cards_dict.get(r, 0)
                        if count >= 2:
                            move.extend([r, r])
                        elif count == 1:
                            move.extend([r, self.wild_rank])
                        else:
                            move.extend([self.wild_rank, self.wild_rank])
                    moves.append(move)
        return moves

    def gen_type_9_serial_pair(self, repeat_num=0):
        """
        生成连对动作（连续对子）：
          - 首先基于真实牌中出现至少两次的牌点生成自然的连对组合；
          - 如果有癞子牌，则调用 gen_serial_pair_with_wild() 补全缺失部分，
          - 将两部分结果合并返回。
        """
        natural_pairs = [r for r, count in self.cards_dict.items() if count >= 2]
        moves = self._gen_serial_moves(natural_pairs, MIN_PAIRS, repeat=2, repeat_num=repeat_num)
        if self.wild_count > 0:
            moves += self.gen_serial_pair_with_wild()
        return moves

    def gen_serial_triple_with_wild(self):
        """
        生成连三动作（连续三条）的补全：
          - 遍历允许的连续牌点序列，对于每个目标三条组合，
          - 如果真实牌中某个牌点不足3张，则用 wild_rank 补全，
          - 例如目标 [8,8,8]，若只有两张8，则输出 [8,8, wild_rank]。
        """
        moves = []
        allowed = list(range(3, 15))
        for length in range(MIN_TRIPLES, len(allowed) + 1):
            for i in range(0, len(allowed) - length + 1):
                seq = allowed[i:i+length]
                valid = True
                missing = 0
                for r in seq:
                    count = self.cards_dict.get(r, 0)
                    if count >= 3:
                        continue
                    elif count > 0:
                        missing += (3 - count)
                    else:
                        missing += 3
                if missing > 0 and missing <= self.wild_count:
                    move = []
                    for r in seq:
                        count = self.cards_dict.get(r, 0)
                        if count >= 3:
                            move.extend([r, r, r])
                        elif count > 0:
                            move.extend([r] * count + [self.wild_rank] * (3 - count))
                        else:
                            move.extend([self.wild_rank] * 3)
                    moves.append(move)
        return moves

    def gen_type_10_serial_triple(self, repeat_num=0):
        """
        生成连三动作（连续三条）：
          - 先基于真实牌生成自然连三组合；
          - 如果有癞子牌，则调用 gen_serial_triple_with_wild() 补全缺失部分，
          - 合并两部分结果返回。
        """
        natural_triples = [r for r, count in self.cards_dict.items() if count >= 3]
        moves = self._gen_serial_moves(natural_triples, MIN_TRIPLES, repeat=3, repeat_num=repeat_num)
        if self.wild_count > 0:
            moves += self.gen_serial_triple_with_wild()
        return moves

    def gen_type_11_serial_3_1(self, repeat_num=0):
        """
        “飞机带单”。
        例如 333-444），然后为每个三条组各附加一张单牌（要求附加的单牌与三条的点数不同），组合后形成飞机带单。
        这种牌型常称为“飞机带翅膀（单）”。：
          - 先生成连三（连续的三条组合）；
          - 对于每个连三组合，从真实牌中选取数量等于该连三组合中不同牌点数的单牌组合，
          - 将连三和选出的单牌组合拼接成动作；
          - 为避免癞子牌重复使用，组合前检查合并后癞子牌的使用总数不超过 self.wild_count。
        """
        serial_3_moves = self.gen_type_10_serial_triple(repeat_num=repeat_num)
        serial_3_1_moves = []
        for s3 in serial_3_moves:
            s3_set = set(s3)
            new_cards = [card for card in self.real_cards_list if card not in s3_set]
            for sub in select(new_cards, len(s3_set)):
                move = s3 + sub
                # 检查该组合中癞子牌使用数量是否合理
                if move.count(self.wild_rank) <= self.wild_count:
                    serial_3_1_moves.append(move)
        return list(k for k, _ in itertools.groupby(serial_3_1_moves))

    def gen_type_12_serial_3_2(self, repeat_num=0):
        """
        “飞机带对子”。
        它的思路是先找出连续的三条组合，然后从其他牌中选取对子，要求选取的对子数量与连续三条组数相同，组合后形成飞机带对子。
        这种牌型常称为“飞机带翅膀（对）”。
          - 先生成连三（连续的三条组合）；
          - 再从真实牌中选取对子组合（对子必须与连三中的牌不同），数量等于连三组合中不同牌点数，
          - 将连三和对子组合拼接，并排序后返回；
          - 同时检查癞子牌总使用数不超过 self.wild_count。
        """
        serial_3_moves = self.gen_type_10_serial_triple(repeat_num=repeat_num)
        serial_3_2_moves = []
        pair_set = sorted([r for r, count in self.cards_dict.items() if count >= 2])
        for s3 in serial_3_moves:
            s3_set = set(s3)
            pair_candidates = [r for r in pair_set if r not in s3_set]
            for sub in select(pair_candidates, len(s3_set)):
                move = sorted(s3 + sub * 2)
                if move.count(self.wild_rank) <= self.wild_count:
                    serial_3_2_moves.append(move)
        return serial_3_2_moves

    def gen_type_13_4_2(self):
        """
        生成“四带二”动作：
          - 对于每个牌点 r，如果自然牌数量为4，则取这4张牌，并从其他真实牌中选取任意两张补全；
          - 如果自然牌数量为3且癞子牌足够，则用1个癞子牌补全成4张，再从其他真实牌中选取2张补全；
          - 利用 groupby 去重后返回所有可能组合。
        """
        result = []
        for r, count in self.cards_dict.items():
            if count == 4:
                four_cards = [r] * 4
                cards_list = [card for card in self.real_cards_list if card != r]
                for sub in select(cards_list, 2):
                    result.append(four_cards + sub)
            elif count == 3 and self.wild_count >= 1:
                four_cards = [r] * 3 + [self.wild_rank]
                cards_list = [card for card in self.real_cards_list if card != r]
                for sub in select(cards_list, 2):
                    result.append(four_cards + sub)
        return list(k for k, _ in itertools.groupby(result))

    def gen_type_14_4_22(self):
        """
        生成“四带二对”动作：
          - 对于每个牌点 r，如果自然牌数量为4，则从其他真实牌中选取两对（对子）补全；
          - 如果自然牌数量为3且癞子牌足够，则用1个癞子牌补全成4张，再带两对；
          - 返回所有可能组合。
        """
        result = []
        for r, count in self.cards_dict.items():
            if count == 4:
                cards_list = [k for k, cnt in self.cards_dict.items() if k != r and cnt >= 2]
                for sub in select(cards_list, 2):
                    result.append([r] * 4 + [sub[0], sub[0], sub[1], sub[1]])
            elif count == 3 and self.wild_count >= 1:
                cards_list = [k for k, cnt in self.cards_dict.items() if k != r and cnt >= 2]
                for sub in select(cards_list, 2):
                    result.append([r] * 3 + [self.wild_rank] + [sub[0], sub[0], sub[1], sub[1]])
        return result

    def gen_moves(self):
        """
        综合调用各类牌型生成函数，返回所有可能的出牌组合列表，
        包括单牌、对子、三条、炸弹、王炸、三带一、三带二、单顺、连对、连三、三带一、三带二、四带二、四带二对。
        """
        moves = []
        moves.extend(self.gen_type_1_single())
        moves.extend(self.gen_type_2_pair())
        moves.extend(self.gen_type_3_triple())
        moves.extend(self.gen_type_4_bomb())
        moves.extend(self.gen_type_5_king_bomb())
        moves.extend(self.gen_type_6_3_1())
        moves.extend(self.gen_type_7_3_2())
        moves.extend(self.gen_type_8_serial_single())
        moves.extend(self.gen_type_9_serial_pair())
        moves.extend(self.gen_type_10_serial_triple())
        moves.extend(self.gen_type_11_serial_3_1())
        moves.extend(self.gen_type_12_serial_3_2())
        moves.extend(self.gen_type_13_4_2())
        moves.extend(self.gen_type_14_4_22())
        return moves

# ----------------------
# 测试用例
if __name__ == '__main__':
    # 示例手牌：设定 4 为癞子牌，测试手牌中包含两张 4（癞子）以及其他自然牌
    test_cards = [3, 3, 5, 5, 5, 7, 8, 9, 10, 11, 4, 4, 12, 12, 12, 6, 6, 6]
    wild_rank = 4  # 指定 4 为癞子牌

    print("测试手牌：", test_cards)
    print("癞子牌：", wild_rank)
    
    mg = MovesGener(test_cards, wild_rank=wild_rank)
    
    print("\n【单牌】")
    print(mg.single_card_moves)
    
    print("\n【对子】")
    print(mg.pair_moves)
    # 例如，若自然牌中只有一个7，则应生成 [7, 4]，明确显示利用癞子牌
    
    print("\n【三条】")
    print(mg.triple_cards_moves)
    # 例如，对于12，如果自然牌数量为2，则生成 [12,12,4]
    
    print("\n【炸弹】")
    print(mg.bomb_moves)
    # 例如，对于12，如果自然牌数量为3，则生成 [12,12,12,4]
    
    print("\n【顺子（单顺）样例】")
    serial_singles = mg.gen_type_8_serial_single()
    print(serial_singles[:5])  # 显示前5个顺子样例，缺失的牌点应以 wild_rank 显示
    
    all_moves = mg.gen_moves()
    print("\n总共生成出牌组合数量：", len(all_moves))
