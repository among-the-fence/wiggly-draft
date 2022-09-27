import random


class GameList:
    def __init__(self):
        self.any_size = ["Hell Let Loose", "Splitgate", "Custom Hero Clash", "Among Us", "Team Fortress 2", "Titanfall 2"]
        self.game_map = {
            2: ["Zero-K", "Phasmophobia", "GTA", "Rocket League"],
            3: ["Zero-K", "Phasmophobia", "GTA", "Rocket League"],
            4: ["Dota", "Siege", "Risk of Rain 2", "Zero-K", "Phasmophobia", "GTA", "Left 4 Dead 2"],
            5: ["Dota", "Siege", "CS:GO", "Halo", "GTA", "Rocket League"],
            6: ["Wiggle", "Halo", "GTA", "Rocket League"],
            7: ["b7", "GTA"],
            8: ["b8", "Left 4 Dead 2"],
            9: ["b9", "c9"],
            10: ["b10", "c10", "Rocket League"]
        }
        for x in self.game_map:
            self.game_map[x].extend(self.any_size)

    def get_rand(self, player_count: int = 4):
        return random.choice(self.game_map[player_count])

    def get_all(self):
        out = ""
        for idx in range(2, 11):
            out = f"{out}: {idx} {self.get_rand(idx)}\n"
        return out


if __name__ == "__main__":
    g = GameList()
    for i in range(2, 11):
        print(i, end=" ")
        for j in range(5):
            print(g.get_rand(i), end=" ")
        print("")
