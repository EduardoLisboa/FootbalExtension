import secrets


class Player:
    def __init__(self, player_id, position, finishing, headingaccuracy, shortpassing, dribling, fkaccuracy, longpassing,
                 acceleration, reactions, stamina, longshots, marking, penalties):
        self.player_id = player_id
        self.position = position
        self.finishing = finishing
        self.headingaccuracy = headingaccuracy
        self.shortpassing = shortpassing
        self.dribling = dribling
        self.fkaccuracy = fkaccuracy
        self.longpassing = longpassing
        self.acceleration = acceleration
        self.reactions = reactions
        self.stamina = stamina
        self.longshots = longshots
        self.marking = marking
        self.penalties = penalties
        self.field_area = None
        self.field_area_value = None
        self.has_ball = False
        self.is_moving = False
        self.selected = False
        self.x = self.y = 0
        self.altered = False
        self.action = ''

    def is_goalkeeper(self):
        return self.field_area == 'goalkeeper'

    def is_defender(self):
        return self.field_area == 'defender'

    def is_midfield(self):
        return self.field_area == 'midfield'

    def is_forward(self):
        return self.field_area == 'forward'

    def with_ball(self, with_ball: bool):
        self.has_ball = with_ball

    def is_moving(self, is_moving: bool):
        self.is_moving = is_moving

    def not_selected(self):
        return self.selected is False

    def move(self, team_index, field):
        self.action = 'Move'
        random_generator = secrets.SystemRandom()

        self.altered = True
        self.is_moving = True

        directions = ['N', 'S', 'E', 'W', 'NE', 'SE', 'NW', 'SW']
        direction_to_move = random_generator.choice(directions)

        if direction_to_move == 'N':
            new_x = self.x
            new_y = random_generator.randint(self.y, min(self.y + 25, 68))
        elif direction_to_move == 'S':
            new_x = self.x
            new_y = random_generator.randint(max(self.y - 25, 0), self.y)
        elif direction_to_move == 'E':
            new_x = random_generator.randint(self.x, min(self.x + 25, 105))
            new_y = self.y
        elif direction_to_move == 'W':
            new_x = random_generator.randint(max(self.x - 25, 0), self.x)
            new_y = self.y
        elif direction_to_move == 'NE':
            new_x = random_generator.randint(self.x, min(self.x + 25, 105))
            new_y = random_generator.randint(self.y, min(self.y + 25, 68))
        elif direction_to_move == 'SE':
            new_x = random_generator.randint(self.x, min(self.x + 25, 105))
            new_y = random_generator.randint(max(self.y - 25, 0), self.y)
        elif direction_to_move == 'NW':
            new_x = random_generator.randint(max(self.x - 25, 0), self.x)
            new_y = random_generator.randint(self.y, min(self.y + 25, 68))
        else:  # SW
            new_x = random_generator.randint(max(self.x - 25, 0), self.x)
            new_y = random_generator.randint(max(self.y - 25, 0), self.y)

        self.x = new_x
        self.y = new_y

        if self.has_ball:
            field.ball_x = self.x
            field.ball_y = self.y

    def pass_ball(self, team_index, field):
        random_generator = secrets.SystemRandom()

        pass_distance = 30
        min_x = int(max(self.x - pass_distance, 0))
        max_x = int(min(self.x + pass_distance, 105))
        min_y = int(max(self.y - pass_distance, 0))
        max_y = int(min(self.y + pass_distance, 68))

        friend_players_in_area = list()
        enemy_players_in_area = list()

        for index, team in enumerate([field.left_team, field.right_team], start=1):
            for player in team.team:
                if player.has_ball:
                    continue

                if min_x <= player.x <= max_x and min_y <= player.y <= max_y:
                    if index == team_index:
                        friend_players_in_area.append(player)
                    else:
                        enemy_players_in_area.append(player)

        if len(friend_players_in_area) > 0:
            receiver_player = random_generator.choice(friend_players_in_area)

            # f1    f2
            # y = ax + b
            divider = abs(self.x - receiver_player.x)
            if divider == 0:
                divider = 1
            a = (abs(self.y - receiver_player.y) / divider)
            b = self.y - (a * self.x)

            enemy_got_ball = False
            if len(enemy_players_in_area) > 0:
                for enemy in enemy_players_in_area:
                    f1 = enemy.y
                    f2 = a * enemy.x + b

                    diff = abs(f1 - f2)

                    # if diff <= 2 and enemy.marking >= self.shortpassing:
                    if diff <= 2:
                        self.altered = True
                        enemy.altered = True
                        enemy_got_ball = True
                        enemy.with_ball(True)
                        field.ball_x = enemy.x
                        field.ball_y = enemy.y

                        if team_index == 1:
                            field.left_team.is_attacking = False
                            field.right_team.is_attacking = True
                        else:
                            field.left_team.is_attacking = True
                            field.right_team.is_attacking = False

                        self.action = 'Pass Ball'
                        enemy.action = 'Steal Ball'

                        self.with_ball(False)

                    if enemy_got_ball:
                        break

            if enemy_got_ball is False:
                receiver_player.altered = True
                self.altered = True

                receiver_player.with_ball(True)
                self.with_ball(False)

                self.action = 'Pass Ball'
                receiver_player.action = 'Receive Ball'

                field.ball_x = receiver_player.x
                field.ball_y = receiver_player.y
        else:
            self.nothing()

    def kick(self, team_index, field):
        # Left = 1, Right = 2
        self.altered = True
        self.action = 'Kick Ball'

        random_generator = secrets.SystemRandom()

        difference = round(100 - float(self.finishing))

        kick_distance = 35

        if team_index == 1:
            new_ball_x = random_generator.randint(self.x, min(self.x + kick_distance, 105))
            new_ball_y = random_generator.randint(31 - difference // 2, 38 + difference // 2)
        else:
            new_ball_x = random_generator.randint(max(self.x - kick_distance, 0), self.x)
            new_ball_y = random_generator.randint(31 - difference // 2, 38 + difference // 2)

        self.with_ball(False)
        field.player_has_ball = False
        field.ball_x = new_ball_x
        field.ball_y = new_ball_y

    def nothing(self):
        self.action = 'Do Nothing'

    def next_move(self, move_str, team_index, field):
        move_dict = {
            'move': self.move,
            'pass': self.pass_ball,
            'kick': self.kick,
            'nothing': self.nothing
        }
        if move_str == 'nothing':
            move_dict[move_str]()
        else:
            move_dict[move_str](team_index, field)

    def compare_players(self, other):
        equal = False
        if self.position == other.position and self.finishing == other.finishing and \
                self.headingaccuracy == other.headingaccuracy and self.shortpassing == other.shortpassing and \
                self.reactions == other.reactions and self.stamina == other.stamina:
            equal = True
        return equal

    def __lt__(self, other):
        return self.field_area_value < other.field_area_value

    def __eq__(self, other):
        return self.field_area_value == other.field_area_value


class Team:
    def __init__(self, team_name):
        self.name = team_name
        self.team = None
        self.current_strategy = None
        self.is_attacking = False

    def create_team(self, players):
        random_generator = secrets.SystemRandom()

        goalkeepers = [x for x in players if x.is_goalkeeper() and x.not_selected()]
        other_players = [x for x in players if not x.is_goalkeeper() and x.not_selected()]

        chosen_players = random_generator.sample(other_players, k=10)
        chosen_players.append(random_generator.choice(goalkeepers))

        pos_counter = {
            'goalkeeper': 0,
            'defender': 0,
            'midfield': 0,
            'forward': 0
        }
        for player in chosen_players:
            pos_counter[player.field_area] += 1
            player.selected = True

        self.team = chosen_players[:]
        self.team.sort()
        self.current_strategy = f'{pos_counter["defender"]}-{pos_counter["midfield"]}-{pos_counter["forward"]}'

    def next_play(self, current_field, friend, foe):
        pass

    def __repr__(self):
        positions = self.team[:]
        player_pos = [x.position for x in positions]
        return f'Current Strategy: {self.current_strategy}\nPlayers: {player_pos}'

    def team_attacking(self):
        return self.is_attacking


class Field:
    def __init__(self, left_team, right_team):
        self.width = 105
        self.height = 68

        self.left_team = left_team
        self.right_team = right_team

        self.ball_x = self.ball_y = 0
        self.player_has_ball = False

        self.left = {
            'gk': {
                'x1': 0,
                'x2': 17,
                'y1': 14,
                'y2': 54
            },
            'df': {
                'x1': 17,
                'x2': 34
            },
            'mid': {
                'x1': 34,
                'x2': 51
            },
            'atk': {
                'x1': 51,
                'x2': 68
            }
        }
        self.right = {
            'gk': {
                'x1': 88,
                'x2': 105,
                'y1': 14,
                'y2': 54
            },
            'df': {
                'x1': 71,
                'x2': 88
            },
            'mid': {
                'x1': 54,
                'x2': 71
            },
            'atk': {
                'x1': 37,
                'x2': 54
            }
        }

    def generate_field(self):
        for player in self.left_team.team:
            x, y = self.get_pos(player, self.left)

            player.x = x
            player.y = y

        for player in self.right_team.team:
            x, y = self.get_pos(player, self.right)

            player.x = x
            player.y = y

    @staticmethod
    def get_pos(player, pos_dict):
        random_generator = secrets.SystemRandom()

        x = y = -1
        if player.is_goalkeeper():
            x = random_generator.randint(pos_dict['gk']['x1'], pos_dict['gk']['x2'])
            y = random_generator.randint(pos_dict['gk']['y1'], pos_dict['gk']['y2'])
        elif player.is_defender():
            x = random_generator.randint(pos_dict['df']['x1'], pos_dict['df']['x2'])
            y = random_generator.randint(0, 68)
        elif player.is_midfield():
            x = random_generator.randint(pos_dict['mid']['x1'], pos_dict['mid']['x2'])
            y = random_generator.randint(0, 68)
        elif player.is_forward():
            x = random_generator.randint(pos_dict['atk']['x1'], pos_dict['atk']['x2'])
            y = random_generator.randint(0, 68)

        return x, y

    def print_field(self):
        player_with_ball = False
        for index, team in enumerate([self.left_team, self.right_team], start=1):
            team_text = f'Left Team: {team.name}' if index == 1 else f'Right Team: {team.name}'
            print(team_text)
            for player in team.team:
                if player.has_ball:
                    player_with_ball = True

                player_pos = f'{player.position:>3}'
                player_xy = f'( {player.x:>2}, {player.y:>2} )'
                player_ball = " - Ball" if player.has_ball else ""
                print(f'    {player_pos} - {player_xy} - {player.action}{player_ball}')

        if not player_with_ball:
            print(f'Ball Position: {self.ball_x}, {self.ball_y}')
