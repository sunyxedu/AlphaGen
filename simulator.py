'''
blank: 0
city: 1
general: 2
mountain: 3
occupied: 0 / 1
------------
New:
0: Unseen Blank
1: Unseen not Blank
2: Seen Blank
3: Seen Uncaptured City
4: Seen Mountain
5: Seen Your Land
6: Seen Your City
7: Seen Your General
8: Seen Opponent's Land
9: Seen Opponent's City
10: Seen Opponent's General
'''
import os
import json
import math
import pickle

Name = ['MeltedToast', 'Mithraaaa']

for name in Name:
    dir="/Users/yuxuan/Documents/Gen_Bot/Replays/Game_Data/" + name
    replays=os.listdir(dir)
    for item in range(len(replays)):
        with open (dir+"/"+replays[item],"r",encoding="utf-8") as file:
            data=json.load(file)

        class Tile:
            def __init__(self,terrain,army,occupied):
                self.terrain=terrain
                self.army=army
                self.occupied=occupied

        class Map:
            width=data["mapWidth"]
            height=data["mapHeight"]
            cities=data["cities"]
            cityArmies=data["cityArmies"]
            generals=data["generals"]
            mountains=data["mountains"]
            
        class Player:
            # vision: 0/1/2
            # 0: Unseen Areas
            # 1: My Tile
            # 2: My Opponent's Tile
            def __init__(self,land,army,vision):
                self.land=land
                self.army=army
                self.vision=vision

        class Turn:
            turn=0
            state=[[-1 for _ in range(Map.width)] for _ in range(Map.height)]
            army=[[-1 for _ in range(Map.width)] for _ in range(Map.height)]
            start=-1
            end=-1
            is50=-1
            myLand=0
            myArmy=0
            opLand=0
            opArmy=0

        turn=0
        index=0
        playerId=0
        turns=[]
        moves=data["moves"]
        usernames=data["usernames"]
        map=[[Tile(0,0,-1) for _ in range(Map.width)] for _ in range(Map.height)]
        player=[Player([],0,[[0 for _ in range(Map.width)] for _ in range(Map.height)]),Player([],0,[[0 for _ in range(Map.width)] for _ in range(Map.height)])]
        info=[Turn() for _ in range(10000)]

        def init():
            for i,general in enumerate(Map.generals):
                map[general//Map.width][general%Map.width]=Tile(2,1,i)
                player[i].land.append(general)

            for i,city in enumerate(Map.cities):
                map[city//Map.width][city%Map.width]=Tile(1,Map.cityArmies[i],-1)

            for i,mountain in enumerate(Map.mountains):
                map[mountain//Map.width][mountain%Map.width]=Tile(3,0,-1)

        def process(move):
            cx,cy=move["start"]//Map.width,move["start"]%Map.width
            nx,ny=move["end"]//Map.width,move["end"]%Map.width
            if move["index"]==0:
                if map[nx][ny].occupied==0:
                    if move["is50"]==0:
                        map[nx][ny].army=map[nx][ny].army+map[cx][cy].army-1
                        map[cx][cy].army=1
                    else:
                        map[nx][ny].army=map[nx][ny].army+math.floor(map[cx][cy].army/2)
                        map[cx][cy].army=math.ceil(map[cx][cy].army/2)
                else:
                    if move["is50"]==0:
                        if map[cx][cy].army>=map[nx][ny].army+2:
                            player[0].land.append(nx*Map.width+ny)
                            if map[nx][ny].occupied==1: player[1].land.remove(nx*Map.width+ny)
                            map[nx][ny].occupied=0
                        map[nx][ny].army=abs(map[nx][ny].army-map[cx][cy].army+1)
                        map[cx][cy].army=1
                    else:
                        if math.floor(map[cx][cy].army/2)>=map[nx][ny].army+1:
                            player[0].land.append(nx*Map.width+ny)
                            if map[nx][ny].occupied==1: player[1].land.remove(nx*Map.width+ny)
                            map[nx][ny].occupied=0
                        map[nx][ny].army=abs(map[nx][ny].army-math.floor(map[cx][cy].army/2))
                        map[cx][cy].army=math.ceil(map[cx][cy].army/2)
            else:
                if map[nx][ny].occupied==1:
                    if move["is50"]==0:
                        map[nx][ny].army=map[nx][ny].army+map[cx][cy].army-1
                        map[cx][cy].army=1
                    else:
                        map[nx][ny].army=map[nx][ny].army+math.floor(map[cx][cy].army/2)
                        map[cx][cy].army=math.ceil(map[cx][cy].army/2)
                else:
                    if move["is50"]==0:
                        if map[cx][cy].army>=map[nx][ny].army+2:
                            player[1].land.append(nx*Map.width+ny)
                            if map[nx][ny].occupied==0:player[0].land.remove(nx*Map.width+ny)
                            map[nx][ny].occupied=1
                        map[nx][ny].army=abs(map[nx][ny].army-map[cx][cy].army+1)
                        map[cx][cy].army=1
                    else:
                        if math.floor(map[cx][cy].army/2)>=map[nx][ny].army+1:
                            player[1].land.append(nx*Map.width+ny)
                            if map[nx][ny].occupied==0:player[0].land.remove(nx*Map.width+ny)
                            map[nx][ny].occupied=1
                        map[nx][ny].army=abs(map[nx][ny].army-math.floor(map[cx][cy].army/2))
                        map[cx][cy].army=math.ceil(map[cx][cy].army/2)
                        
        def renew():
            player[0].army,player[1].army=0,0
            player[0].vision,player[1].vision=[[0 for _ in range(Map.width)] for _ in range(Map.height)],[[0 for _ in range(Map.width)] for _ in range(Map.height)]
            for tile in player[0].land:
                player[0].army+=map[tile//Map.width][tile%Map.width].army
                player[0].vision[tile//Map.width][tile%Map.width]=1
                dx,dy=[0,1,0,-1,1,1,-1,-1],[1,0,-1,0,1,-1,1,-1]
                for i in range(8):
                    nx,ny=tile//Map.width+dx[i],tile%Map.width+dy[i]
                    if nx>=0 and nx<Map.height and ny>=0 and ny<Map.width and player[0].vision[nx][ny]!=1:
                        player[0].vision[nx][ny]=2
                
            for tile in player[1].land:
                player[1].army+=map[tile//Map.width][tile%Map.width].army
                player[1].vision[tile//Map.width][tile%Map.width]=1
                dx,dy=[0,1,0,-1,1,1,-1,-1],[1,0,-1,0,1,-1,1,-1]
                for i in range(8):
                    nx,ny=tile//Map.width+dx[i],tile%Map.width+dy[i]
                    if nx>=0 and nx<Map.height and ny>=0 and ny<Map.width and player[1].vision[nx][ny]!=1:
                        player[1].vision[nx][ny]=2

            for k in range(2):
                if k!=playerId: continue
                info[turn].myArmy=player[k].army
                info[turn].myLand=len(player[k].land)
                info[turn].opArmy=player[1-k].army
                info[turn].opLand=len(player[1-k].land)
                for i in range(Map.height):
                    for j in range(Map.width):
                        if player[k].vision[i][j]==0 and (map[i][j].terrain==0 or map[i][j].terrain==2):
                            info[turn].state[i][j]=0
                        elif player[k].vision[i][j]==0 and (map[i][j].terrain==1 or map[i][j].terrain==3):
                            info[turn].state[i][j]=1
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==0 and map[i][j].occupied==-1:
                            info[turn].state[i][j]=2
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==1 and map[i][j].occupied==-1:
                            info[turn].state[i][j]=3
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==3:
                            info[turn].state[i][j]=4
                        elif player[k].vision[i][j]==1 and map[i][j].terrain==0:
                            info[turn].state[i][j]=5
                        elif player[k].vision[i][j]==1 and map[i][j].terrain==1:
                            info[turn].state[i][j]=6
                        elif player[k].vision[i][j]==1 and map[i][j].terrain==2:
                            info[turn].state[i][j]=7
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==0 and map[i][j].occupied==1-k:
                            info[turn].state[i][j]=8
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==1 and map[i][j].occupied==1-k:
                            info[turn].state[i][j]=9
                        elif player[k].vision[i][j]==2 and map[i][j].terrain==2 and map[i][j].occupied==1-k:
                            info[turn].state[i][j]=10
                        
                        if (player[k].vision[i][j]==1 or player[k].vision[i][j]==2) and (map[i][j].terrain==0 or map[i][j].terrain==1 or map[i][j].terrain==2):
                            info[turn].army[i][j]=map[i][j].army

        def nextTurn():
            global turn
            global index
            for i in range(2):
                if index>=len(moves): continue
                if turn==moves[index]["turn"]:
                    if moves[index]["index"]==playerId:
                        info[turn].start=moves[index]["start"]
                        info[turn].end=moves[index]["end"]
                        info[turn].is50=moves[index]["is50"]
                    process(moves[index])
                    index+=1

            global turns
            map_info=[]
            for x in range(Map.height):
                for y in range(Map.width):
                    tmp=[info[turn].state[x][y]]
                    if player[playerId].vision[x][y]!=0:
                        if map[x][y].terrain==3:
                            tmp.append(0)
                        else:
                            tmp.append(info[turn].army[x][y])
                    else:
                        tmp.append(-1)

                    map_info.append(tmp)

            is_first=0
            if (playerId==0 and turn%2==0) or (playerId==1 and turn%2==1): is_first=1
            res1 = [[0 for _ in range(25)] for _ in range(25)]
            res2 = [[0 for _ in range(25)] for _ in range(25)]
            res = [[0 for _ in range(25)] for _ in range(25)]
            for x in range(25):
                for y in range(25):
                    if (x<=Map.height and y<=Map.width):
                        res1[x][y]=info[turn].state
                        res2[x][y]=info[turn].army
                    else:
                        info[turn].state=1
                        info[turn].army=0
                    

            turns.append([info[turn].state, info[turn].army])
            # turns.append([turn,is_first,data["mapWidth"],data["mapHeight"],info[turn].myArmy,info[turn].myLand,info[turn].opArmy,info[turn].opLand,map_info,info[turn].start,info[turn].end,info[turn].is50])

        def endTurn():
            global turn
            if turn%2==0:
                for city in Map.cities:
                    if map[city//Map.width][city%Map.width].occupied!=-1:
                        map[city//Map.width][city%Map.width].army+=1
                        
                for general in Map.generals:
                    map[general//Map.width][general%Map.width].army+=1
                    
                if turn%50==0:
                    for i in range(2):
                        for tile in player[i].land:
                            map[tile//Map.width][tile%Map.width].army+=1

        def main():
            init()
            global playerId
            global turn
            global index

            turn=0
            for i in range(2):
                if usernames[i]==name:
                    playerId=i

            renew()
            
            if moves:
                for i in range(moves[len(moves)-1]["turn"]+1):
                    nextTurn()
                    turn+=1
                    endTurn()
                    renew()
                    
                new_data={}
                new_data["id"]=data["id"]
                new_data["turns"]=turns
                with open("/Users/yuxuan/Documents/Gen_Bot/Replays/Match_Data/"+name+'/'+f"{replays[item][:-5]}.pkl","wb") as file:
                    pickle.dump(new_data, file)
            else:
                print(f"Warning: No moves found for replay {replays[item]}")
            
            # print(f"{item}: {replays[item]}, turns: {data["moves"][len(data["moves"])-1]["turn"]}")

            

        main()  