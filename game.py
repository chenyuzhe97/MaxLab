class Game:
    def __init__(self, debug=1):
        self.debug = debug
        self.jiang_li = 0
        self.game_name = 0
        self.result = (0, "ping")
        self.rule = Rule()
        self.guize = self.rule.color_size
        self.score_table = {"nao": [], "ren": []}

    def load_game(self):
        self.score_table = {"nao": [], "ren": []}

    def insert_table(self, a1,a2):
        self.score_table["nao"].append(a1)
        self.score_table["ren"].append(a2)

    def record_table(self, nao_pai, ren_pai):
        game_round = len(nao_pai)
        for count in range(game_round):
            card_nao = nao_pai[count]
            card_ren = ren_pai[count]
            if self.guize[card_nao] > self.guize[card_ren]:
                self.insert_table(1, -1)
            elif self.guize[card_nao] < self.guize[card_ren]:
                self.insert_table(-1, 1)
            else:
                self.insert_table(0, 0)
        return self.score_table

    def game1(self, nao_pai, ren_pai):
        self.load_game()
        score_table = self.record_table(nao_pai, ren_pai)
        result = self.rule.rule1(score_table)
        self.jiang_li = 0
        self.print(result)
        return result

    def game2(self, nao_pai, ren_pai):
        self.load_game()
        score_table = self.record_table(nao_pai, ren_pai)
        result = self.rule.rule2(score_table)
        self.jiang_li = 0
        self.print(result)
        return result

    def game3(self, nao_pai, ren_pai):
        self.load_game()
        score_table = self.record_table(nao_pai, ren_pai)
        result = self.rule.rule3(score_table)
        self.jiang_li = 0
        self.print(result)
        return result

    def game4(self, nao_pai, ren_pai):
        self.load_game()
        score_table = self.record_table(nao_pai, ren_pai)
        result = self.rule.rule4(score_table)
        self.print(result)

        if self.game_name == "4.1":
            self.jiang_li = 1
        elif self.game_name == "4.2":
            self.jiang_li = 2
        elif self.game_name == "4.3":
            self.jiang_li = 3
        elif self.game_name == "4.4":
            self.jiang_li = 4
        elif self.game_name == "4.5":
            self.jiang_li = 5

        return result

    def game5(self, nao_pai, ren_pai):
        self.load_game()
        score_table = self.record_table(nao_pai, ren_pai)
        result = self.rule.rule5(score_table)
        self.print(result)
        return result

    def get_reward(self):
        return self.jiang_li

    def get_jiangli(self):
        return self.jiang_li

    def start_game(self, game_name, nao_pai, ren_pai):
        self.game_name = game_name
        game_mapping = {
            '1': 'game1', '5.1': 'game1', '6.1': 'game1', '6.2': 'game1', '6.3': 'game1',
            '2': 'game2',
            '3': 'game3',
            '4.1': 'game4', '4.2': 'game4', '4.3': 'game4', '4.4': 'game4', '4.5': 'game4',
            '5.2': 'game5', '6.4': 'game5', '6.5': 'game5', '6.6': 'game5',
        }
        game_type = game_mapping.get(game_name)
        if game_type:
            game_method = getattr(self, game_type, None)
            if game_method:
                return game_method(nao_pai, ren_pai)
            else:
                ValueError(f"这个游戏编号还没写：{game_type}")
        else:
            ValueError("游戏编号输错了！")

    def print(self, content):
        if self.debug == 1:
            print(content)


class Rule:
    def __init__(self):
        self.color_size = {'red_1': 3, 'red_2': 4, 'black_1': 1, 'black_2': 2}

    def rule1(self, score_table):
        if score_table["nao"][0] > score_table["ren"][0]:
            return 1, "win"
        elif score_table["nao"][0] < score_table["ren"][0]:
            return -1, "lose"
        return 0, "draw"

    def rule2(self, score_table):
        if score_table["nao"][0] < score_table["ren"][0]:
            return 1, "win"
        elif score_table["nao"][0] > score_table["ren"][0]:
            return -1, "lose"
        return 0, "draw"

    def rule3(self, score_table):
        if score_table["nao"][0] > score_table["ren"][0] and score_table["nao"][1] > score_table["ren"][1]:
            return 1, "win"
        elif score_table["nao"][0] < score_table["ren"][0] and score_table["nao"][1] < score_table["ren"][1]:
            return -1, "lose"
        return 0, "draw"


    def rule4(self, score_table):
        if score_table["nao"][0] > score_table["ren"][0]:
            return 1, "win"
        elif score_table["nao"][0] < score_table["ren"][0]:
            return -1, "lose"
        return 0, "draw"

    def rule5(self, score_table):
        if score_table["nao"][0] > score_table["ren"][0] and score_table["nao"][1] > score_table["ren"][1]:
            return 1, "win"
        elif score_table["nao"][0] < score_table["ren"][0] and score_table["nao"][1] < score_table["ren"][1]:
            return -1, "lose"
        return 0, "draw"
