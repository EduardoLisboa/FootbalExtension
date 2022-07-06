from screen import *
from soccer import *
import secrets
import copy
import math


def read_and_preprocess_data():
    players = list()
    with open('data.csv', 'r') as f:
        for index, line in enumerate(f.readlines()):
            if index == 0:
                continue

            line = line.replace('\n', '')

            info = line.split(',')[1:]

            players.append(Player(*info))

    field_pos = {
        'goalkeeper': ['GK'],
        'defender': ['RWB', 'LB', 'CB', 'RCB', 'LWB', 'LCB', 'RB'],
        'midfield': ['RCM', 'CM', 'LCM', 'CAM', 'LM', 'RW', 'LAM', 'RM', 'RAM', 'LW', 'RDM', 'CDM', 'LDM'],
        'forward': ['LS', 'CF', 'LF', 'RF', 'RS', 'ST']
    }

    for key, pos_list in field_pos.items():
        for player in players:
            if player.position in pos_list:
                player.field_area = key

                if key == 'goalkeeper':
                    player.field_area_value = 0
                elif key == 'defender':
                    player.field_area_value = 1
                elif key == 'midfield':
                    player.field_area_value = 2
                else:
                    player.field_area_value = 3

    return players


def prepare_field(left_team_name='PSG', right_team_name='BARCELONA'):
    players = read_and_preprocess_data()

    left_team = Team(left_team_name)
    left_team.create_team(players)

    right_team = Team(right_team_name)
    right_team.create_team(players)

    field = Field(left_team, right_team)
    field.generate_field()

    return field


def generate_playing_position(field):
    random_generator = secrets.SystemRandom()

    teams = ['Left', 'Right']
    players = [i for i in range(0, 11)]

    coin_toss = random_generator.randint(0, 1)

    if coin_toss:
        chosen_team = random_generator.choice(teams)
        if chosen_team == 'Left':
            chosen_player = random_generator.choice(players)
            field.left_team.team[chosen_player].with_ball(True)
            field.ball_x = field.left_team.team[chosen_player].x
            field.ball_y = field.left_team.team[chosen_player].y
        else:
            chosen_player = random_generator.choice(players)
            field.right_team.team[chosen_player].with_ball(True)
            field.ball_x = field.right_team.team[chosen_player].x
            field.ball_y = field.right_team.team[chosen_player].y
    else:
        ball_x = random_generator.randint(0, field.width)
        ball_y = random_generator.randint(0, field.height)

        got_ball = False
        for team in [field.left_team, field.right_team]:
            for player in team.team:
                if ball_x-1 <= player.x <= ball_x+1 and ball_y-1 <= player.y <= ball_y+1:
                    player.with_ball(True)
                    team.is_attacking = True
                    field.ball_x = player.x
                    field.ball_y = player.y
                    got_ball = True
                    break
            if got_ball:
                break

        if not got_ball:
            field.ball_x = ball_x
            field.ball_y = ball_y

    return field


def print_all_fields(current_position, message):
    if isinstance(current_position, list):
        for index, field in enumerate(current_position, start=1):
            msg = f'-=-=-=- Field {message} {index:<2} -=-=-=-'
            print(msg)
            field.print_field()
            print('-=' * (len(msg) // 2), end='-\n\n')
    else:
        msg = f'-=-=-=- Field {message} -=-=-=-'
        print(msg)
        current_position.print_field()
        print('-=' * (len(msg) // 2), end='-\n\n')


def make_move(position_before):
    position_after = copy.deepcopy(position_before)
    random_generator = secrets.SystemRandom()
    possibilities_with_ball = [
        'move',
        'pass',
        'kick',
        'nothing'
    ]
    possibilities_without_ball = [
        'move',
        'nothing'
    ]

    weights = (4, 1)

    for index, team in enumerate([position_after.left_team, position_after.right_team], start=1):
        for player in team.team:
            if player.altered:
                continue

            if player.has_ball:
                move_str = random_generator.choice(possibilities_with_ball)
            else:
                move_str = random_generator.choices(possibilities_without_ball, weights=weights, k=1)

            player.next_move(move_str[0] if isinstance(move_str, list) else move_str, index, position_after)

    got_ball = False
    ball_x = position_after.ball_x
    ball_y = position_after.ball_y
    for team in [position_after.left_team, position_after.right_team]:
        for player in team.team:
            if ball_x + 1 >= player.x >= ball_x - 1 and ball_y + 1 >= player.y >= ball_y - 1:
                player.with_ball(True)
                team.is_attacking = True
                position_after.ball_x = player.x
                position_after.ball_y = player.y
                got_ball = True
                break
        if got_ball:
            break

    return position_after


def adaptation(init_population):
    field_before = init_population[0]
    fields_after = init_population[1][:]

    adaptations_list = [0 for _ in range(0, len(fields_after))]

    for field_index, field_after in enumerate(fields_after):
        # We had the ball and lost it
        if field_before.left_team.is_attacking and not field_after.left_team.is_attacking:
            adaptations_list[field_index] -= 1000
        # We didn't have the ball and acquired it
        elif not field_before.left_team.is_attacking and field_after.left_team.is_attacking:
            adaptations_list[field_index] += 1000
        # We had the ball and kept it
        elif field_before.left_team.is_attacking and field_after.left_team.is_attacking:
            adaptations_list[field_index] += 1000

        player_ball = False
        for player in field_after.left_team.team:
            if player.has_ball:
                player_ball = True

            # Player passed the ball
            if player.action == 'Pass Ball':
                stolen_ball = False
                # Enemy stole the ball
                for enemy_player in field_after.right_team.team:
                    if enemy_player.action == 'Steal Ball':
                        stolen_ball = True
                        break
                if stolen_ball:
                    adaptations_list[field_index] -= 100
                else:
                    player_ball = True

            # Player received the ball
            if player.action == 'Receive Ball':
                player_ball = True
                adaptations_list[field_index] += 100

        # The ball moved closer to the goal
        if field_after.ball_x > field_before.ball_x:
            adaptations_list[field_index] += 200
        else:
            adaptations_list[field_index] -= 50

        if field_before.player_has_ball is False:
            if field_after.player_has_ball is True and player_ball:
                adaptations_list[field_index] += 1000
            else:
                players_pos_before = list()
                players_pos_after = list()
                for player in field_before.left_team.team:
                    players_pos_before.append((player.x, player.y))
                for player in field_after.left_team.team:
                    players_pos_after.append((player.x, player.y))
                players_pos = list(zip(players_pos_before, players_pos_after))
                for player_pos in players_pos:
                    x_before, y_before = player_pos[0]
                    x_after, y_after = player_pos[1]

                    dist_before = math.sqrt((x_before - field_before.ball_x)**2 + (y_before - field_before.ball_y)**2)
                    dist_after = math.sqrt((x_after - field_after.ball_x)**2 + (y_after - field_after.ball_y)**2)

                    if dist_after < dist_before:
                        adaptations_list[field_index] += 200

    return list(zip(adaptations_list, fields_after))


def mutation(population, position_before):
    original_fields = [x[1] for x in population]
    fields_adapt = [x[0] for x in population]
    fields = [copy.deepcopy(x) for x in original_fields]

    random_generator = secrets.SystemRandom()
    possibilities_with_ball = [
        'move',
        'pass',
        'kick',
        'nothing'
    ]
    possibilities_without_ball = [
        'move',
        'nothing'
    ]

    position_after = copy.deepcopy(position_before)
    for field_index, field in enumerate(fields):
        if fields_adapt[field_index] > 2500:
            mutation_chance = 5
        else:
            mutation_chance = 20

        received_ball = False
        for team_index, team in enumerate([field.left_team, field.right_team], start=1):
            for player_index, player in enumerate(team.team):
                if team_index == 1 and player.action == 'Receive Ball':
                    received_ball = True

        for team_index, team in enumerate([field.left_team, field.right_team], start=1):
            for player_index, player in enumerate(team.team):
                will_mutate = random_generator.randint(1, 100)
                if will_mutate <= mutation_chance:
                    if team_index == 1:
                        new_player = copy.deepcopy(position_before.left_team.team[player_index])
                    else:
                        new_player = copy.deepcopy(position_before.right_team.team[player_index])

                    if new_player.has_ball:
                        if received_ball:
                            continue
                        move_str = random_generator.choice(possibilities_with_ball)
                    else:
                        move_str = random_generator.choices(possibilities_without_ball, weights=[6, 1], k=1)

                    new_player.next_move(
                        move_str[0] if isinstance(move_str, list) else move_str, team_index, position_after
                    )
                    team.team[player_index] = new_player
                else:
                    pass

    return fields


def main():
    field = prepare_field()

    field_copy = copy.deepcopy(field)
    position_before = generate_playing_position(field_copy)

    positions_after = list()
    while len(positions_after) < 20:
        new_position = make_move(position_before)
        positions_after.append(new_position)

    init_population = [position_before, positions_after[:]]

    init_pop_adapt = adaptation(init_population)

    init_pop_adapt.sort(key=lambda x: x[0], reverse=True)

    population = init_pop_adapt[:]

    for generation in range(1, 101):
        print(f'GENERATION {generation}')

        original_population = population[:]

        print('Mutating Population')
        mutated_population = mutation(population, position_before)

        mutated_pop = [position_before, mutated_population[:]]

        print('Calculating mutated population adaptions')
        mutated_pop_adapt = adaptation(mutated_pop)
        mutated_pop_adapt.sort(key=lambda x: x[0], reverse=True)

        print('Creating new population')
        new_population = mutated_pop_adapt[:10]
        new_population.extend(original_population[:5])
        aux = list()
        while len(aux) < 5:
            new_position = make_move(position_before)
            aux.append(new_position)
        aux_pop = [position_before, aux[:]]
        aux_adapt = adaptation(aux_pop)
        new_population.extend(aux_adapt)

        new_population.sort(key=lambda x: x[0], reverse=True)
        population = new_population[:]

    print('\n\nFINISHED PROCESSING\n\n')

    population.sort(key=lambda x: x[0], reverse=True)
    best_adaptation = population[0][0]
    best_population = population[0][1]

    print_all_fields(field_copy, 'Before')
    print(f'Best adaptation: {best_adaptation}')
    print_all_fields(best_population, 'After')
    DrawField(field_copy,best_population)


if __name__ == '__main__':
    main()
