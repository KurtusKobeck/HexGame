#Generic Hexagonal Board Game Simulation Enviroment (GHBGSE)
#I wanted to create a means for my friends and I to play board game night across the country after I moved. This project is my ongoing effort to make that possible.
#It can already visualize and track the game state of a game of GHBG! I am working on smarter NPCs.
#
#day18: implemented buyObject() methods for roads, development cards and settlements which require sufficient resources to execute. If ran without the right cards to pay for them, they return -3 with no effect
#Day19: added a devRollForTurn() function to force a roll of my choosing for testing. Number is chosen via shell input.
#implemented cities.
#implemented development cards
#Bug: when building roads 72,71 and potentially more roads along the far right border, the road north of the placed road is not being appended to canBuild[1]... I'll fix this tomorrow. Its the second time it's popped up...
#A week later (life happened)
#Day 20: figured out hwo to split the dev menu up from the turn menu in the simulation window.
#Day 21: added player.handSize() to return the current # of cards in hand
#Begun working on the npc script
#Implemented a simulation.determineIdealRobberPos() def to pick a best place to put the robber for each NPC. Implemented at complexity level 1. See toChooseBestRobberPos.txt for explanation of levels 2 and 3.
#implemented a simulation.determineBestSettlementPos() def to determine which settlementNum has the highest net yield. Current iteration ignores the "value" of the resources in question and always selects the location closest to the top left
#corner rather than, say, trying to make sure it can access wood, lumber, wheat and sheep.
#Day 22: Implemented a slightly smarter bestSettlement finder which prioritizes total yield, then the sum of yield diversity (# of rolls the settlement yields resources on) and resource desireability(gives priority to resources you don't have yet and extra priority
# in order of wheat>ore>brick>lumber>wool) to encourage the most diverse and consistent of yields available from the highest yielding options.
#Day 23: I have been away from the project for nearly 7 weeks due to relocating across the country. I am going to be getting back into it, though.
#finished implementing the test for NPCs setting up a 4 bot game of catan. (random road placement rather than smart road placement) complete with resources being distributed on the placement of the second settlement.

#To-Do:
#Implement a check to ensure the road building road position chosen is legal in playAdevelopmentCard()
#npc requirement: Each player need to calculate their ideal position for the robber each time a settlement/city is placed. This value is called idealRobberPos and is an int 0-18 representing the 0-indexed hex of choice.
#NPC requirement: new bestBuildableSettlementPos(playerID) which returns the best pos the player can currently build
#NPC requirement: new bestTargetSettlementPos(playerID) which returns the settlementPos of the best settlement the player can build with the fewest number of roads built plus the roadNums required to reach it.
#change the robber roll on 7 moveTheRobber(robberizer,newpos) to treat the current turn's player as the robberizer instead of random.randint(0,3)
#abstract and implement turns,
#implement a rudementary NPC.
#improve UI
#currently, the reaction to 7 being rolled is for every player with 8 or more cards in hand to discard half rounded down. This is non-standard, as
#players are intended to be able to choose which resources they discard. I will need to add a "choose what to keep" system at some point.



#Issues to be fixed:
#   Unlike IDLE V3.11, the native Python IDE, Visual Studio Code doesn't implicitly handle the tkinter mainloop. Need to explicitly invoke mainloop so that those who haven't configured their VSC for Python can still run this project.
#   For now, run the code using your latest version of IDLE. If you have Python installed on your machine than it ought to have came with your installation of Python.

#|----------------------------------------------------------------------------------------|
#Populate from pool with dropout:
#A drop table is a complete list of all the possible outcomes of an event
import random;
random.seed(a=None,version=2)
class dropTable:#works as intended
    def __init__(self,table):
        self.table=table;
    def pullADrop(self):#works as intended!
        if(len(self.table)==0):
            return -1
        rn=random.randint(0,len(self.table)-1);
        pull=self.table[rn];
        self.table=self.table[0:rn]+self.table[rn+1:];
        return pull
#|----------------------------------------------------------------------------------------|
from tkinter import *
#|----------------------------------------------------------------------------------------|
class player:
    #The player class exists to aggregate information about the resources available to the player
    #in one easy to access location: the player's object. The simulation stores a copy of the data with
    #it's positional context intact. The player only needs to remember what the board state means for their
    #resources and actions while the simulation keeps up with the state of the board. The simulation verifies that
    #an action is possible, the player simply keeps track of the results.
    def __init__(self,name):
        self.name=str(name)
        self.victoryPoints=0
        self.resourceIndex={0:"Brick",1:"Wheat",2:"Wool",3:"Ore",4:"Lumber"}
        self.costIndex={"development":[0,1,1,1,0],"road":[1,0,0,0,1],"settlement":[1,1,1,0,1],"city":[0,2,0,3,0]}
        #tracks which ports you have unlocked; 3for1=0,2brickfor=1,2wheatfor=2,2woolfor=3,2orefor=4,2lumberfor=5
        self.harbors=[0,0,0,0,0,0]
        #current resources [brick,wheat,wool,ore,lumber]
        self.hand=[0,0,0,0,0]
        #10 to win the game, 2 for longest road, 2 for largest army, 1 for a
        #settlement, 2 for a city and 1 per development point development card. 
        self.developmentPoints=0;
        #tracks what resources and how many of them this player receives when a given number 2-12 is rolled. This chart is updated whenever a player places a settlement or city.
        self.yieldOnRoll=[0,0,[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],
                          [0,0,0,0,0],0,[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],
                          [0,0,0,0,0],[0,0,0,0,0]]
        #Track the coordinates of your settlements
        self.settlements=[]
        #Track the coordinates of your cities
        self.cities=[]
        #Track the locations of your existing roads
        self.roads=[]
        #canBuild[0] refers to unclaimed settlementNodes at least 2 units away from another settlement which your roads can access, canBuild[1] refers to unclaimed roadNodes adjacent to your existing roads.
        self.canBuild=[[],[]]#you can build cities wherever you've got a settlement so as long as I track settlements I don't need to track where cities can be built
        #holds the development cards a player has built (but not revealed.)
        self.developmentCardsBuilt=[0,0,0,0,0]#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        self.developmentCardsBuiltThisTurn=[0,0,0,0,0]#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        #tracks the development cards a player has revealed, a player can reveal 1 card per turn.
        #holds the development cards a player has played
        self.developmentCardsPlayed=[0,0,0,0,0]#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
    def goFish(self):
        words = ['Player ',self.name,'\n','bricks:',str(self.hand[0]),' wheat:',str(self.hand[1]),' wool:',str(self.hand[2]),' ore:',str(self.hand[3]),' lumber:',str(self.hand[4]),'\n','Dev Cards played: ',str(self.developmentCardsPlayed),' Dev Cards saved: ',str(self.developmentCardsBuilt)]
        return ' '.join(str(word) for word in words)
    def handSize(self):
        cardsInHand=0;
        for resourceType in self.hand:
            cardsInHand+=resourceType;  # number of that resource card in hand
        return cardsInHand
    def postTrade(self):
        print("wip");
    def considerTrade(self):
        print("WIP");
    def useBankOrPorts(self,these,forThat):
        #3for1=0,2brickfor=1,2wheatfor=2,2woolfor=3,2orefor=4,2lumberfor=5 ;this=0-4, forThat=0-4
        #check for specialty port, else check for 3:1, else use 4:1, finally check for 2,3 or 4 of [this] kind before removing them from hand[this] and adding one of [forThat]
        bestOffer=self.bestDeal(these)
        if(self.hand[these]>=bestOffer):#checks for enough cards to use either the bank or harbors to trade
           self.hand[these]-=bestOffer
           self.hand[forThat]+=1
           print("Player",self.name,"has traded",bestOffer,"x",self.resourceIndex[these],"with the bank for",self.resourceIndex[forThat],"at a rate of",bestOffer," to 1")
        else:
            print("Player",self.name,"doesn't have enough",self.resourceIndex[these],"to trade with the bank for",self.resourceIndex[forThat],"using your best available rate of exchange, ",bestOffer)
    def yields(self,rollNum):
        #player.yields(rollNum) adds to the player's hand the contents of self.yieldOnRoll[rollNum]
        i=0
        for resourceType in self.hand:
            self.hand[i]+=self.yieldOnRoll[rollNum][i]
            i+=1
    def updateBuildableReg(self,thingNums,taken,roadsOrSettlements):#taken is a booleans for determining whether a number is being added or removed from the list. roadsOrSettlements=0 means roads, =1 means settlements
        #will almost always be used in conjunction with: settlementNodes[2] to pull valid roads from a given settlement at the start of the game and roadConnections[0] and [1] to pull roadNums and settlementNums by association with roadNums
        if(taken):
            for item in thingNums:
                if self.canBuild.count(item)>0:
                    self.canBuild[roadsOrSettlements].remove(item)
        else:
            for item in thingNums:
                self.canBuild[roadsOrSettlements].append(item)
        self.canBuild.sort()
    #def placeRoad(self):
    #def placeSettlement(self):
    #def placeCity(self):
    def sevenWasRolled(self): #Tested and confirmed to be working as intended
        cardsInHand=0;
        cards=[];
        num=0;
        for resourceType in self.hand:
            cardsInHand+=resourceType;  # number of that resource card in hand
            i=0;
            while(i<resourceType):
                cards.extend([num]);   #list where every card is represented as it's resource type ex. [0,0,2,2,2,3,4] 0-4 are valid types.
                i+=1;
            num+=1                      #increments the resourcetype number to be added to the list for the next iteration
        if(cardsInHand>7):
            handTable=dropTable(cards);
            i=((cardsInHand/2)+(cardsInHand/2)%1);
            for jay in range (int(i),cardsInHand):  #i= half of handsize rounded down, handsize-i= number of cards to be discarded
                handTable.pullADrop();
            newHand=[0,0,0,0,0];
            for card in handTable.table:
                newHand[card]+=1
            self.hand=newHand
    def robberized(self):
        if(self.hand[0]!=0 or self.hand[1]!=0 or self.hand[2]!=0 or self.hand[3]!=0 or self.hand[4]!=0):
            cards=[]
            num=0
            for resourceType in self.hand:
                i=0
                while(i<resourceType):
                    cards.extend([num])
                    i+=1
                num+=1
            handTable=dropTable(cards)
            plunderedResource=handTable.pullADrop()
            self.hand[plunderedResource]=self.hand[plunderedResource]-1
            #print(plunderedResource)
            return plunderedResource
        else:
            print("You cannot steal from those who have nothing!")
            return -2
    def robberize(self,plunder):
        self.hand[plunder]=self.hand[plunder]+1
    def canAfford(self,thing):#cost is a list [x,x,x,x,x] containing the cost of the item. This function returns true if it is possible to meet this cost using the bank/ports and cards in hand
        deficit=[0,0,0,0,0]
        missingCards=0
        totalCardsInHand=0
        if(thing in self.costIndex):
            cost=self.costIndex[thing]
            for i in range(0,5):
                totalCardsInHand+=self.hand[i]
                if(self.hand[i]-cost[i]>-1):#If you have enough to cover this portion of the cost, you have no deficit of this resource
                    deficit[i]=0
                else:
                    deficit[i]=abs(self.hand[i]-cost[i])
                    missingCards+=deficit[i]
            surplus=[0,0,0,0,0]
            totalSpareCards=0
            wildCards=0
            offerings=[0,0,0,0,0]
            for i in range(0,5):
                remainder=self.hand[i]-cost[i]
                if(remainder>0):#if there are any resources left, toss them into the remainder
                    surplus[i]=remainder
                    totalSpareCards+=remainder
                    bestRoE=self.bestDeal(i)#returns the best rate of exchange for the chosen resource between all available harbors and the bank
                    while(remainder>=bestRoE):#while you've got enough to trade for anything,
                        wildCards+=1
                        remainder=remainder-bestRoE
                        offerings[i]=offerings[i]+1
            #print("you have",wildCards,"wildcards and need",missingCards,"to afford",deficit,"and you have these cards to trade",totalSpareCards,surplus,"with",totalCardsInHand,"cards in hand")
            if(missingCards==0):
                print("You can afford a",thing,"using cards in hand.")
                return True
            elif(wildCards>=missingCards):
                print("You can trade up to",offerings[0],"brick,",offerings[1],"wheat,",offerings[2],"wool,",offerings[3],"ore and",offerings[4],"lumber with the bank or your ports for the cards you need to build")
                return offerings
            elif(totalSpareCards>missingCards):
                print("You would need to trade and have enough spare resources to make an offer")
                return surplus,deficit
            else:#another elif to check for what 2sparesfor1 and 1for1 trades you can offer the other players to attempt to build it.
                print("You cannot afford a",thing)
        else:
            print("Thats not a road, settlement, city or development!")
            return -1
    def bestDeal(self,card):
        bestOffer=4
        if(self.harbors[0]==1):#Checks for 3for1 harbor
            bestOffer=3
        if(self.harbors[card+1]==1):#every time a settlement is placed on a harbor, player.harbors[harborType]=1, thus this checks for the corresponding specialty harbor
            bestOffer=2
        return bestOffer
    def yieldSummary(self):
        yieldSummary=[0,0,0,0,0]
        for roll in self.yieldOnRoll:
            if roll!=0:
                for i in range(0,5):
                    yieldSummary[i]+=roll[i]
        return yieldSummary
#|----------------------------------------------------------------------------------------|



class simulation:
    def __init__(self):
        self.robTheRobber=0
        self.imReg()
        self.menuGen()
        self.resetTheBoard()
    def imReg(self):
        #Files must be loaded in both the init and the reset function, thus it is easier to make 2 def calls to one registry than to maintain 2 identical registries.
        self.window=Tk()
        self.window.destroy()
        self.window=Tk()
        #self.hex = [PhotoImage(file='desertHex.png'),PhotoImage(file='quarryHex.png'),PhotoImage(file='fieldHex.png'),PhotoImage(file='pastureHex.png'),PhotoImage(file='mountainHex.png'),PhotoImage(file='forestHex.png')]
        self.hex = [PhotoImage(file='desertHex.png'),PhotoImage(file='quarryHex.png'),PhotoImage(file='fieldHex.png'),PhotoImage(file='pastureHex.png'),PhotoImage(file='mountainHex.png'),PhotoImage(file='forestHex.png')]
        self.oceanHex = PhotoImage(file='oceanHex.png')
        self.roads = [[PhotoImage(file='player_1_Road0.png'),PhotoImage(file='player_1_Road1.png'),PhotoImage(file='player_1_Road2.png')],[PhotoImage(file='player_2_Road0.png'),PhotoImage(file='player_2_Road1.png'),PhotoImage(file='player_2_Road2.png')],[PhotoImage(file='player_3_Road0.png'),PhotoImage(file='player_3_Road1.png'),PhotoImage(file='player_3_Road2.png')],[PhotoImage(file='player_4_Road0.png'),PhotoImage(file='player_4_Road1.png'),PhotoImage(file='player_4_Road2.png')]]
        self.ports = [[PhotoImage(file='3for1HarborNW.png'),PhotoImage(file='3for1HarborN.png'),PhotoImage(file='3for1HarborNE.png'),PhotoImage(file='3for1HarborSE.png'),PhotoImage(file='3for1HarborS.png'),PhotoImage(file='3for1HarborSW.png')],
                      [PhotoImage(file='brickHarborNW.png'),PhotoImage(file='brickHarborN.png'),PhotoImage(file='brickHarborNE.png'),PhotoImage(file='brickHarborSE.png'),PhotoImage(file='brickHarborS.png'),PhotoImage(file='brickHarborSW.png')],
                      [PhotoImage(file='wheatHarborNW.png'),PhotoImage(file='wheatHarborN.png'),PhotoImage(file='wheatHarborNE.png'),PhotoImage(file='wheatHarborSE.png'),PhotoImage(file='wheatHarborS.png'),PhotoImage(file='wheatHarborSW.png')],
                      [PhotoImage(file='woolHarborNW.png'),PhotoImage(file='woolHarborN.png'),PhotoImage(file='woolHarborNE.png'),PhotoImage(file='woolHarborSE.png'),PhotoImage(file='woolHarborS.png'),PhotoImage(file='woolHarborSW.png')],
                      [PhotoImage(file='oreHarborNW.png'),PhotoImage(file='oreHarborN.png'),PhotoImage(file='oreHarborNE.png'),PhotoImage(file='oreHarborSE.png'),PhotoImage(file='oreHarborS.png'),PhotoImage(file='oreHarborSW.png')],
                      [PhotoImage(file='lumberHarborNW.png'),PhotoImage(file='lumberHarborN.png'),PhotoImage(file='lumberHarborNE.png'),PhotoImage(file='lumberHarborSE.png'),PhotoImage(file='lumberHarborS.png'),PhotoImage(file='lumberHarborSW.png')]]
        self.tokens = [0,0,PhotoImage(file='token2.png'),PhotoImage(file='token3.png'),PhotoImage(file='token4.png'),PhotoImage(file='token5.png'),PhotoImage(file='token6.png'),0,PhotoImage(file='token8.png'),PhotoImage(file='token9.png'),
                       PhotoImage(file='token10.png'),PhotoImage(file='token11.png'),PhotoImage(file='token12.png')]
        self.robberToken=PhotoImage(file='robberV2.png')
        self.houses=[PhotoImage(file='player_1_settlementV2.png'),PhotoImage(file='player_2_settlementV2.png'),PhotoImage(file='player_3_settlementV2.png'),PhotoImage(file='player_4_settlementV2.png')]
        self.cities=[PhotoImage(file='player_1_cityV2.png'),PhotoImage(file='player_2_cityV2.png'),PhotoImage(file='player_3_cityV2.png'),PhotoImage(file='player_4_cityV2.png')]
        self.diceImages = [PhotoImage(file='1Dice.png'),PhotoImage(file='2Dice.png'),PhotoImage(file='3Dice.png'),PhotoImage(file='4Dice.png'),
                           PhotoImage(file='5Dice.png'),PhotoImage(file='6Dice.png'),PhotoImage(file='rollDice.png')]
        self.resourceIndex={0:"Brick",1:"Wheat",2:"Wool",3:"Ore",4:"Lumber"}
        self.WIDTH=1500;
        self.HEIGHT=1230;
        self.N=98.5;
        self.GRID=1.73*self.N;
        self.GRIDx=1.47*self.N;
        self.GRIDy=0.866*self.N;
        self.GRID2=0.5*self.N;
        self.GRID2s=0.5*self.N-30;
        self.window.title=("Settlers of Katan")
        self.canvas=Canvas(self.window,width=self.WIDTH,height=self.HEIGHT)
        self.canvas.pack()
        #V2: 1-72 x [x,y,0-2] 0=horizontal, 1=+45', 2=-45'
        self.roadGridCoords = [[1*self.GRIDx-6,2*self.GRID+6,1],[1*self.GRIDx-6,2.5*self.GRID+6,2],[1*self.GRIDx-6,3*self.GRID+6,1],[1*self.GRIDx-6,3.5*self.GRID+6,2],[1*self.GRIDx-6,4*self.GRID+6,1],#5
                               [1*self.GRIDx-6,4.5*self.GRID+6,2],[1*self.GRIDx+self.GRID2+9,2*self.GRID-6,0],[1*self.GRIDx+self.GRID2+9,3*self.GRID-6,0],[1*self.GRIDx+self.GRID2+9,4*self.GRID-6,0],[1*self.GRIDx+self.GRID2+9,5*self.GRID-6,0],#10
                               [2*self.GRIDx-6,1.5*self.GRID+6,1],[2*self.GRIDx-6,2*self.GRID+6,2],[2*self.GRIDx-6,2.5*self.GRID+6,1],[2*self.GRIDx-6,3*self.GRID+6,2],[2*self.GRIDx-6,3.5*self.GRID+6,1],#15
                               [2*self.GRIDx-6,4*self.GRID+6,2],[2*self.GRIDx-6,4.5*self.GRID+6,1],[2*self.GRIDx-6,5*self.GRID+6,2],[2*self.GRIDx+self.GRID2+9,1.5*self.GRID-6,0],[2*self.GRIDx+self.GRID2+9,2.5*self.GRID-6,0],#20
                               [2*self.GRIDx+self.GRID2+9,3.5*self.GRID-6,0],[2*self.GRIDx+self.GRID2+9,4.5*self.GRID-6,0],[2*self.GRIDx+self.GRID2+9,5.5*self.GRID-6,0],[3*self.GRIDx-6,1*self.GRID+6,1],[3*self.GRIDx-6,1.5*self.GRID+6,2],#25
                               [3*self.GRIDx-6,2*self.GRID+6,1],[3*self.GRIDx-6,2.5*self.GRID+6,2],[3*self.GRIDx-6,3*self.GRID+6,1],[3*self.GRIDx-6,3.5*self.GRID+6,2],[3*self.GRIDx-6,4*self.GRID+6,1],#30
                               [3*self.GRIDx-6,4.5*self.GRID+6,2],[3*self.GRIDx-6,5*self.GRID+6,1],[3*self.GRIDx-6,5.5*self.GRID+6,2],[3*self.GRIDx+self.GRID2+9,1*self.GRID-6,0],[3*self.GRIDx+self.GRID2+9,2*self.GRID-6,0],#35
                               [3*self.GRIDx+self.GRID2+9,3*self.GRID-6,0],[3*self.GRIDx+self.GRID2+9,4*self.GRID-6,0],[3*self.GRIDx+self.GRID2+9,5*self.GRID-6,0],[3*self.GRIDx+self.GRID2+9,6*self.GRID-6,0],[4*self.GRIDx-6,1*self.GRID+6,2],#40
                               [4*self.GRIDx-6,1.5*self.GRID+6,1],[4*self.GRIDx-6,2*self.GRID+6,2],[4*self.GRIDx-6,2.5*self.GRID+6,1],[4*self.GRIDx-6,3*self.GRID+6,2],[4*self.GRIDx-6,3.5*self.GRID+6,1],#45
                               [4*self.GRIDx-6,4*self.GRID+6,2],[4*self.GRIDx-6,4.5*self.GRID+6,1],[4*self.GRIDx-6,5*self.GRID+6,2],[4*self.GRIDx-6,5.5*self.GRID+6,1],[4*self.GRIDx+self.GRID2+9,1.5*self.GRID-6,0],#50
                               [4*self.GRIDx+self.GRID2+9,2.5*self.GRID-6,0],[4*self.GRIDx+self.GRID2+9,3.5*self.GRID-6,0],[4*self.GRIDx+self.GRID2+9,4.5*self.GRID-6,0],[4*self.GRIDx+self.GRID2+9,5.5*self.GRID-6,0],[5*self.GRIDx-6,1.5*self.GRID+6,2],#55
                               [5*self.GRIDx-6,2*self.GRID+6,1],[5*self.GRIDx-6,2.5*self.GRID+6,2],[5*self.GRIDx-6,3*self.GRID+6,1],[5*self.GRIDx-6,3.5*self.GRID+6,2],[5*self.GRIDx-6,4*self.GRID+6,1],#60
                               [5*self.GRIDx-6,4.5*self.GRID+6,2],[5*self.GRIDx-6,5*self.GRID+6,1],[5*self.GRIDx+self.GRID2+9,2*self.GRID-6,0],[5*self.GRIDx+self.GRID2+9,3*self.GRID-6,0],[5*self.GRIDx+self.GRID2+9,4*self.GRID-6,0],#65
                               [5*self.GRIDx+self.GRID2+9,5*self.GRID-6,0],[6*self.GRIDx-6,2*self.GRID+6,2],[6*self.GRIDx-6,2.5*self.GRID+6,1],[6*self.GRIDx-6,3*self.GRID+6,2],[6*self.GRIDx-6,3.5*self.GRID+6,1],#70
                               [6*self.GRIDx-6,4*self.GRID+6,2],[6*self.GRIDx-6,4.5*self.GRID+6,1]]#1-72
        #hexGridCoords stores the coordinates for a given hex grid's sprite. Intended for use in rendering the board iteratively.
        self.hexGridCoords=[[0,self.GRID],[0,self.GRID*2],[0,self.GRID*3],[self.GRIDx,self.GRIDy],[self.GRIDx,self.GRID+self.GRIDy],[self.GRIDx,2*self.GRID+self.GRIDy],[self.GRIDx,3*self.GRID+self.GRIDy],
                            [2*self.GRIDx,0],[2*self.GRIDx,self.GRID],[2*self.GRIDx,2*self.GRID],[2*self.GRIDx,3*self.GRID],[2*self.GRIDx,4*self.GRID],[3*self.GRIDx,self.GRIDy],[3*self.GRIDx,self.GRID+self.GRIDy],
                            [3*self.GRIDx,self.GRID*2+self.GRIDy],[3*self.GRIDx,self.GRID*3+self.GRIDy],[4*self.GRIDx,self.GRID],[4*self.GRIDx,self.GRID*2],[4*self.GRIDx,self.GRID*3]]
        
        #settlementGridCoords holds the screenspace coordinates for the various settlements. Cities use the same table and just kinda... sit on top of the settlements, visually speaking, as removing them doesn't seem to be possible without redrawing the map
        self.settlementGridCoords = [[self.GRID2,self.GRID],[0,self.GRID*1.5],[self.GRID2,self.GRID*2],[0,self.GRID*2.5],[self.GRID2,self.GRID*3],[0,self.GRID*3.5],[self.GRID2,self.GRID*4],[self.GRIDx+self.GRID2,self.GRID*0.5],[self.GRIDx,self.GRID],[self.GRIDx+self.GRID2,self.GRID*1.5],#10
                                     [self.GRIDx,self.GRID*2],[self.GRIDx+self.GRID2,self.GRID*2.5],[self.GRIDx,self.GRID*3],[self.GRIDx+self.GRID2,self.GRID*3.5],[self.GRIDx,self.GRID*4],[self.GRIDx+self.GRID2,self.GRID*4.5],[self.GRIDx*2+self.GRID2,0],[self.GRIDx*2,self.GRID*0.5],#18
                                     [self.GRIDx*2+self.GRID2,self.GRID*1],[self.GRIDx*2,self.GRID*1.5],[self.GRIDx*2+self.GRID2,self.GRID*2],[self.GRIDx*2,self.GRID*2.5],[self.GRIDx*2+self.GRID2,self.GRID*3],[self.GRIDx*2,self.GRID*3.5],[self.GRIDx*2+self.GRID2,self.GRID*4],#25
                                     [self.GRIDx*2,self.GRID*4.5],[self.GRIDx*2+self.GRID2,self.GRID*5],[self.GRIDx*3,self.GRID*0.0],[self.GRIDx*3+self.GRID2,self.GRID*0.5],[self.GRIDx*3,self.GRID*1],[self.GRIDx*3+self.GRID2,self.GRID*1.5],[self.GRIDx*3,self.GRID*2],[self.GRIDx*3+self.GRID2,self.GRID*2.5],
                                     [self.GRIDx*3,self.GRID*3],[self.GRIDx*3+self.GRID2,self.GRID*3.5],[self.GRIDx*3,self.GRID*4],[self.GRIDx*3+self.GRID2,self.GRID*4.5],[self.GRIDx*3,self.GRID*5],[self.GRIDx*4,self.GRID*0.5],[self.GRIDx*4+self.GRID2,self.GRID*1],[self.GRIDx*4,self.GRID*1.5],
                                     [self.GRIDx*4+self.GRID2,self.GRID*2],[self.GRIDx*4,self.GRID*2.5],[self.GRIDx*4+self.GRID2,self.GRID*3],[self.GRIDx*4,self.GRID*3.5],[self.GRIDx*4+self.GRID2,self.GRID*4],[self.GRIDx*4,self.GRID*4.5],[self.GRIDx*5,self.GRID*1],[self.GRIDx*5+self.GRID2,self.GRID*1.5],
                                     [self.GRIDx*5,self.GRID*2],[self.GRIDx*5+self.GRID2,self.GRID*2.5],[self.GRIDx*5,self.GRID*3],[self.GRIDx*5+self.GRID2,self.GRID*3.5],[self.GRIDx*5,self.GRID*4]]#
        
        #There are 9 ocean tiles and 9 port tiles each requiring an [x,y] definition in their respective GridCoord lists. The ports contain an additional variable, direction, used to determine which orientation of port image to use.
        self.oceanGridCoords = [[self.GRIDx*2,self.GRID*0.5],[self.GRIDx*4,self.GRID*0.5],[self.GRIDx*6,self.GRID*1.5],[self.GRIDx*6,self.GRID*3.5],[self.GRIDx*5,self.GRID*5],[self.GRIDx*3,self.GRID*6],[self.GRIDx*1,self.GRID*5],[0,self.GRID*3.5],[0,self.GRID*1.5]]
        #orientation: 0=NW, 1=N, 2=NE, 3=SE, 4=S, 5=SW. (x,y,orientation,harbor type)
        self.harborGridCoords = [[self.GRIDx*3,0,4,0],[self.GRIDx*5,self.GRID,5,0],[self.GRIDx*6,self.GRID*2.5,5,0],[self.GRIDx*6,self.GRID*4.5,0,0],[self.GRIDx*4,self.GRID*5.5,1,0],[self.GRIDx*2,self.GRID*5.5,1,0],[0,self.GRID*4.5,2,0],[0,self.GRID*2.5,3,0],[self.GRIDx,self.GRID,3,0]]
        
    def resetTheBoard(self):
        #resetPlayers(cities, settlements, roads,
                        #development points, largest army,
                        #longest road, resources in hand,
                        #port access)
        #numBots=int(input("How many bots in this match? Pick a number 0-4 "))
        numBots=0
        self.players = [player(1), player(2), player(3), player(4)]
        self.botReg=[False,False,False,False]#True when the player is being handled as a bot by the simulation, false when the player is a person operating the UI.
        if(numBots>-1 and numBots <5):
            for i in range(0,numBots):
                self.botReg[3-i]=True
        #Turn order priority: 0-3
        self.turnOrder=0;
        #resetDevelopmentCardDeck
        #cityGrid[0]: 12x11 grid of valid locations to place a settlement or city on the map, used for ensuring that cities and settlements are at least 2 roads apart when placed.
        self.cityGrid=[[0],[0]];
        #cityGrid[z][y][x]
        #self.cityGrid[0] = [[0,0,0,0,0,1,1,0,0,0,0,0],
        #                    [0,0,0,1,1,0,0,1,1,0,0,0],
        #                    [0,1,1,0,0,1,1,0,0,1,1,0],
        #                    [1,0,0,1,1,0,0,1,1,0,0,1],
        #                    [0,1,1,0,0,1,1,0,0,1,1,0],
        #                    [1,0,0,1,1,0,0,1,1,0,0,1],
        #                    [0,1,1,0,0,1,1,0,0,1,1,0],
        #                    [1,0,0,1,1,0,0,1,1,0,0,1],
        #                    [0,1,1,0,0,1,1,0,0,1,1,0],
        #                    [0,0,0,1,1,0,0,1,1,0,0,0],
        #                    [0,0,0,0,0,1,1,0,0,0,0,0]]
        #V2: each node-1 points to the settlementNode index for it's settlementNode
        self.cityGrid[0] = [[0,0,0,0,0,17,28,0,0,0,0,0],
                            [0,0,0,8,18,0,0,29,39,0,0,0],
                            [0,1,9,0,0,19,30,0,0,40,48,0],
                            [2,0,0,10,20,0,0,31,41,0,0,49],
                            [0,3,11,0,0,21,32,0,0,42,50,0],
                            [4,0,0,12,22,0,0,33,43,0,0,51],
                            [0,5,13,0,0,23,34,0,0,44,52,0],
                            [6,0,0,14,24,0,0,35,45,0,0,53],
                            [0,7,15,0,0,25,36,0,0,46,54,0],
                            [0,0,0,16,26,0,0,37,47,0,0,0],
                            [0,0,0,0,0,27,38,0,0,0,0,0]]
        #cityGrid[1] 12x11 grid of 0-8 integers which track which player has built where: 1=player1, 2=player2, 3=player3, 4=player4.
        self.cityGrid[1] = [[0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0,0,0,0,0,0]]
        #contains the cityGrid coordinates for each of the 54 settlement nodes in [y][x] order and a list of the hexes which the node borders of length 1-3
        self.settlementNodes=[[0],[0],[0],[0]];
        #settlementNodes[0] holds [y,x] coordinates within the cityGrid[0][y][x] table there are 54 settlement/city nodes on the map, each player has 5 settlements and 4 cities.
        self.settlementNodes[0] = [[2,1],[3,0],[4,1],[5,0],[6,1],[7,0],[8,1],
                                [1,3],[2,2],[3,3],[4,2],[5,3],[6,2],[7,3],[8,2],[9,3],
                                [0,5],[1,4],[2,5],[3,4],[4,5],[5,4],[6,5],[7,4],[8,5],[9,4],[10,5],
                                [0,6],[1,7],[2,6],[3,7],[4,6],[5,7],[6,6],[7,7],[8,6],[9,7],[10,6],
                                [1,8],[2,9],[3,8],[4,9],[5,8],[6,9],[7,8],[8,9],[9,8],
                                [2,10],[3,11],[4,10],[5,11],[6,10],[7,11],[8,10]]
        #settlementNodes[1] holds the 0 indexed values for the resourceTiles[[],...] 0-18 lookup chart. Used for determining which resources a given node yields in a given game.
        self.settlementNodes[1] = [[0],[0],[0,1],[1],[1,2],[2],[2],[3],[3,0],[0,3,4],[0,1,4],[1,4,5],#12
                                   [1,2,5],[2,5,6],[2,6],[6],[7],[3,7],[3,7,8],[3,4,8],[4,8,9],[4,5,9],[5,9,10],[5,6,10],#24
                                   [6,10,11],[6,11],[11],[7],[7,12],[7,8,12],[8,12,13],[8,9,13],[9,13,14],[9,10,14],[10,14,15],[10,11,15],#36
                                   [11,15],[11],[12],[12,16],[12,13,16],[13,16,17],[13,14,17],[14,17,18],[14,15,18],[15,18],[15],[16],#48
                                   [16],[16,17],[17],[17,18],[18],[18]]#54
        #settlementNodes[2] holds the roadNum values for the roads adjacent to it. Used for determining which roads can be built from a given settlement.
        self.settlementNodes[2] = [[1,7],[1,2],[2,3,8],[3,4],[4,5,9],[5,6],[6,10],[11,19],[7,11,12],[12,13,20],[8,13,14],[14,15,21],#12
                                   [9,15,16],[16,17,22],[10,17,18],[18,23],[24,34],[19,24,25],[25,26,35],[20,26,27],[27,28,36],[21,28,29],[29,30,37],[22,30,31],#24
                                   [31,32,38],[23,32,33],[33,39],[34,40],[40,41,50],[35,41,42],[42,43,51],[36,43,44],[44,45,52],[37,45,46],[46,47,53],[38,47,48],#36
                                   [48,49,54],[39,49],[50,55],[55,56,63],[51,56,57],[57,58,64],[52,58,59],[59,60,65],[53,60,61],[61,62,66],[54,62],[63,67],#48
                                   [67,68],[64,68,69],[69,70],[65,70,71],[71,72],[66,72]]#54
        #associates the linear settlement number with the harbor it borders for use in adding access to the harbor to the player when the settlement is placed. references self.harborGridCoords[i][3]
        self.settlementNodes[3] = [0,0,8,8,0,7,7,9,9,0,0,0,0,0,0,6,1,0,0,0,0,0,0,0,0,6,0,#1-27
                                   1,0,0,0,0,0,0,0,0,5,0,2,2,0,0,0,0,0,0,5,0,0,3,3,0,4,4]#28-54
        #Used to reference all the settlements a robber is touching by the 0-18 hexNum of the hex the robber has been placed on.
        self.hexNum2SettlementNum = [[1,2,3,9,10,11],[3,4,5,11,12,13],[5,6,7,13,14,15],[8,9,10,18,19,20],[10,11,12,20,21,22],[12,13,14,22,23,24],#0-5
                                     [14,15,16,24,25,26],[17,18,19,28,29,30],[19,20,21,30,31,32],[21,22,23,32,33,34],[23,24,25,34,35,36],[25,26,27,36,37,38],#6-11
                                     [29,30,31,39,40,41],[31,32,33,41,42,43],[33,34,35,43,44,45],[35,36,37,45,46,47],[40,41,48,49,50],[42,43,44,50,51,52],[44,45,46,52,53,54]]#12-18
        #.sNCC settlementNodeConversionChart: converts col,row to settlementNum, used to place settlements using the a-k,1-6 board grid
        self.sNCC = [[0,0,1,2,3,4,5,6,7,0,0],
                     [0,8,9,10,11,12,13,14,15,16,0],
                     [17,18,19,20,21,22,23,24,25,26,27],
                     [28,29,30,31,32,33,34,35,36,37,38],
                     [0,39,40,41,42,43,44,45,46,47,0],
                     [0,0,48,49,50,51,52,53,54,0,0]]
        self.settlementNum2ColRow=[[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[3,1],[3,2],[3,3],
                                   [3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[4,1],[4,2],[4,3],[4,4],[4,5],[4,6],[4,7],[4,8],[4,9],[4,10],[4,11],
                                   [5,2],[5,3],[5,4],[5,5],[5,6],[5,7],[5,8],[5,9],[5,10],[6,3],[6,4],[6,5],[6,6],[6,7],[6,8],[6,9]]
        self.roadConnections=[[0],[0]]
        #roadConnections[0] contains a list of lists of the roads connected to themself; used for determining where players can and cannot place roads
        self.roadConnections[0]=[[2,7],[1,3,8],[2,4,8],[3,5,9],[4,6,9],[5,10],[1,11,12],[2,3,13,14],[4,5,15,16],[6,17,18],[7,12,19],[7,11,13,20],[8,12,14,20],[8,13,15,21],[9,14,16,21],[9,15,17,22],[10,16,18,22],[10,17,23],[11,24,25],[12,13,26,27],[14,15,28,29],[16,17,30,31],#1-22
                                 [18,32,33],[19,25,34],[19,24,26,35],[20,25,27,35],[20,26,28,36],[21,27,29,36],[21,28,30,37],[22,29,31,37],[22,30,32,38],[23,31,33,38],[23,32,39],[24,40],[25,26,41,42],[27,28,43,44],[29,30,45,46],[31,32,47,48],[33,49],[34,41,50],[35,40,42,50],#23-41
                                 [35,41,43,51],[36,42,44,51],[36,43,45,52],[37,44,46,52],[37,45,47,53],[38,46,48,53],[38,47,49,54],[39,48,50,54],[40,41,55],[42,43,56,57],[44,45,58,59],[46,47,60,61],[48,49,62],[50,56,63],[51,55,57,63],[51,56,58,64],[52,57,59,64],[52,58,60,65],#42-59
                                 [53,59,61,65],[53,60,62,66],[54,61,63,66],[55,56,67],[57,58,68,69],[59,60,70,71],[61,62,72],[63,68],[64,67,69],[64,68,70],[65,69,71],[65,70,72],[66,71]]#60-72
        #roadConnections[1] contains a list 1-72 of the settlmentNode1-54 which are connected to a given road tile; used for determining where players can and cannot place settlements
        self.roadConnections[1]=[[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[1,9],[3,11],[5,13],[7,15],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14],[14,15],[15,16],[8,18],[10,20],
                                 [12,22],[14,24],[16,26],[17,18],[18,19],[19,20],[20,21],[21,22],[22,23],[23,24],[24,25],[25,26],[26,27],[17,28],[19,30],[21,32],[23,34],[25,36],[27,38],[28,29],
                                 [29,30],[30,31],[31,32],[32,33],[33,34],[34,35],[35,36],[36,37],[37,38],[29,39],[31,41],[33,43],[35,45],[37,47],[39,40],[40,41],[41,42],[42,43],[43,44],[44,45],
                                 [45,46],[46,47],[40,48],[42,50],[44,52],[46,54],[48,49],[49,50],[50,51],[51,52],[52,53],[53,54]]#1-72
        #Stores the player who placed each of the roads
        #self.roadGrid = [[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],
        #              [0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],
        #              [0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],
        #              [0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]]#1-72
        self.roadGrid = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                         0,0,0,0,0,0,0,0,0,0,0,0]#1-72
        self.colRow2RoadNum = [[0,0,1,2,3,4,5,6,0,0],
                               [0,7,8,9,10,0,0,0,0,0],
                               [0,11,12,13,14,15,16,17,18,0],
                               [19,20,21,22,23,0,0,0,0,0],
                               [24,25,26,27,28,29,30,31,32,33],
                               [34,35,36,37,38,39,0,0,0,0],
                               [40,41,42,43,44,45,46,47,48,49],
                               [50,51,52,53,54,0,0,0,0,0],
                               [0,55,56,57,58,59,60,61,62,0],
                               [0,63,64,65,66,0,0,0,0,0],
                               [0,0,67,68,69,70,71,72,0,0]]#11x10
        self.roadNum2ColRow = [[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[2,2],[2,3],[2,4],[2,5],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[4,1],[4,2],[4,3],[4,4],[4,5],[5,1],[5,2],[5,3],[5,4],[5,5],[5,6],
                               [5,7],[5,8],[5,9],[5,10],[6,1],[6,2],[6,3],[6,4],[6,5],[6,6],[7,1],[7,2],[7,3],[7,4],[7,5],[7,6],[7,7],[7,8],[7,9],[7,10],[8,1],[8,2],[8,3],[8,4],[8,5],[9,2],[9,3],[9,4],[9,5],
                               [9,6],[9,7],[9,8],[9,9],[10,2],[10,3],[10,4],[10,5],[11,3],[11,4],[11,5],[11,6],[11,7],[11,8]]#0-indexed

        #Used to check cityGrid slots for cities relative to the coordinates of the resource hex tiles stored in self.tileNumberCoordinates
        #self.resourceHexGridFilter=[[-1,0],[0,-1],[0,1],[1,-1],[1,1],[2,0]]
        
        #resourceTiles: 0-18, these tiles contain 2 digits; [resource type, roll to receive];
        self.resourceTiles = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        
        #roadGrid: First digit determines type of slot; 0=unplaceable location, 1=right leaning slot, 2=left leaning slot, 3=vertical slot
        #          Second digit stores the player # whose built on it 0=empty, 1=player 1, 2=player 2...
        #self.roadGrid = [[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[0,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[0,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[0,0]],
        #                 [[0,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[0,0],[0,0]],
        #                 [[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0]],
        #                 [[0,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[3,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[0,0],[2,0],[1,0],[2,0],[1,0],[2,0],[1,0],[0,0],[0,0],[0,0],[0,0]],
        #                 [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]]

        #roadConnectivityFilters: used for determining where players can place roads; 0=left leaning, 1=right leaning, 2=vertical
        self.roadConnectivityFilters = [[[0,1,0],[1,0,1],[0,0,1]],[[0,0,1],[1,0,1],[0,1,0]],[[1,1,0],[0,0,0],[1,1,0]]]

        #Token drop tables & resource tile drop tables are as defined in the board game, [1x2,2x[3-11],1x12] for tokens and 1 desert, 3 quarries, 4 fields, 4 pastures, 3 mountains and 4 forests for resource tiles.
        #desert=0, quarry=1, field=2, pasture=3, mountain=4, forest=5
        self.tokenTable=dropTable([2,3,3,4,4,5,5,6,6,8,8,9,9,10,10,11,11,12]);
        self.resourceTable=dropTable([0,1,1,1,2,2,2,2,3,3,3,3,4,4,4,5,5,5,5]);
        self.developmentCardTable=dropTable([0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,2,2,3,3,4,4]);#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        #hand resource order index [lumber, bricks, wheat, wool, ore]
        #3for1=0,2lumberfor=1,2brickfor=2,2wheatfor=3,2woolfor=4,2orefor=5
        self.harbors=dropTable([0,0,0,0,1,2,3,4,5])

        #instance the robber. He will be placed inside the desert hex tile during self.populateTheBoard()
        self.robberPos=0;
        #instances the largest army.
        self.largestArmy=(2,'')#[0] is the current count to beat, [1] is who holds it.

        #Fills the board with resource tiles and resource tokens.
        self.populateTheHexes();
        #Populates the hexes of the board.
        self.populateTheBoard();
        self.placeRobberToken()
        #self.rollForTurn()
        #Fixes the GUI at the start of the game without rolling the dice.
        self.updateScoreboard()
        self.alphaDice.destroy()
        self.betaDice.destroy()
        self.alphaDice=Button(self.window,image=self.diceImages[0],command=lambda: self.rollForTurn(),borderwidth=0)
        self.alphaDice.pack(side='left')
        self.betaDice=Button(self.window,image=self.diceImages[0],command=lambda: self.rollForTurn(),borderwidth=0)
        self.betaDice.pack(anchor=E,side='left')

    def menuGen(self):
        self.players = [player(1), player(2), player(3), player(4)]
        #Adds menus to the window.
        self.mainMenu=Menu(self.window)
        self.window.config(menu=self.mainMenu)
        self.gameMenu=Menu(self.mainMenu)
        self.mainMenu.add_cascade(label="Game",menu=self.gameMenu)
        self.gameMenu.add_command(label='Generate new board (dev: Visual Effect Only)',command=self.repopulateTheBoardButtonCommand)
        self.gameMenu.add_command(label='Reset the game',command=self.resetTheBoard)
        #self.gameMenu.add_separator()
        self.gameTurnMenu=Menu(self.mainMenu)
        self.mainMenu.add_cascade(label="turn",menu=self.gameTurnMenu)
        self.gameTurnMenu.add_command(label='Roll for turn',command=self.rollForTurn)
        self.gameTurnMenu.add_command(label='Roll for turn (dev)',command=self.devRollForTurn)
        self.ddType=StringVar()
        self.ddCol=StringVar()
        self.ddRow=StringVar()
        self.ddPlayer=StringVar()
        self.optMenu1=OptionMenu(self.window,self.ddType,'road','settlement','City','Development Card').pack(side='left')
        self.optMenu2=OptionMenu(self.window,self.ddCol,'1','2','3','4','5','6','7','8','9','10','11').pack(side='left')
        self.optMenu3=OptionMenu(self.window,self.ddRow,'1','2','3','4','5','6','7','8','9','10','11').pack(side='left')
        self.optMenu4=OptionMenu(self.window,self.ddPlayer,'1','2','3','4').pack(side='left')
        self.buildButton=Button(self.window,text="Build",command=self.inputReader,borderwidth=0).pack(side='left')
        self.player1Hand=Label(self.window,text=self.players[0].goFish())
        self.player1Hand.pack(side='top',anchor=NE)
        self.player2Hand=Label(self.window,text=self.players[1].goFish())
        self.player2Hand.pack(side='right',anchor=NE)
        self.player3Hand=Label(self.window,text=self.players[2].goFish())
        self.player3Hand.pack(side='left',anchor=NE)
        self.player4Hand=Label(self.window,text=self.players[3].goFish())
        self.player4Hand.pack(side='bottom',anchor=NE)
        self.alphaDice=Button(self.window,image=self.diceImages[6],command=self.rollForTurn,borderwidth=0)
        self.alphaDice.pack(side='left')
        self.betaDice=Button(self.window,image=self.diceImages[6],command=self.rollForTurn,borderwidth=0)
        self.betaDice.pack(anchor=E,side='right')
    def inputReader(self):
        if(len(self.ddType.get())>0 and len(self.ddCol.get())>0 and len(self.ddRow.get())>0 and len(self.ddPlayer.get())>0):
            #print("{}{}{}{}".format(self.ddType.get(),self.ddCol.get(),self.ddRow.get(),self.ddPlayer.get()))
            if(self.ddType.get()=="road"):
                self.placeRoad(int(self.ddCol.get()),int(self.ddRow.get()),int(self.ddPlayer.get())-1)
            if(self.ddType.get()=="settlement"):
                self.placeSettlement(int(self.ddCol.get()),int(self.ddRow.get()),int(self.ddPlayer.get())-1)
            if(self.ddType.get()=="Development Card"):
                self.drawADevelopmentCard(int(self.ddPlayer.get())-1)
    def populateTheBoard(self):
        i=0;
        for hex in self.resourceTiles:
            self.canvas.create_image(self.GRIDx+self.hexGridCoords[i][0],self.GRID+self.hexGridCoords[i][1],image=self.hex[hex[0]],anchor=NW);
            if(hex[1]>0):
                self.canvas.create_image(self.GRIDx+self.hexGridCoords[i][0]+self.GRIDy-23.4,self.GRID+self.hexGridCoords[i][1]+self.GRIDy-35,image=self.tokens[hex[1]],anchor=NW);
            i+=1
        for tile in self.harborGridCoords:
            self.canvas.create_image(tile[0],tile[1],image=self.ports[tile[3]][tile[2]],anchor=NW)
        for fish in self.oceanGridCoords:
            self.canvas.create_image(fish[0],fish[1],image=self.oceanHex,anchor=NW)
        
    def populateTheHexes(self):
        i=0;
        for hex in self.resourceTiles:
            hex[0]=self.resourceTable.pullADrop();
            if(hex[0]>0):
                hex[1]=self.tokenTable.pullADrop();
            else:
                self.robberPos=i;
                self.placeRobberToken()
            i+=1;
        i=0;
        for tile in self.harborGridCoords:
            self.harborGridCoords[i][3]=self.harbors.pullADrop()
            i+=1
            

    def repopulateTheBoardButtonCommand(self):  #Does not reset the game!
        self.resourceTiles = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        self.tokenTable=dropTable([2,3,3,4,4,5,5,6,6,8,8,9,9,10,10,11,11,12]);
        self.resourceTable=dropTable([0,1,1,1,2,2,2,2,3,3,3,3,4,4,4,5,5,5,5]);
        self.harbors=dropTable([0,0,0,0,1,2,3,4,5])
        self.populateTheHexes()
        self.populateTheBoard()
                
        
    def rollForTurn(self):
        self.dice1=random.randint(1,6)
        self.dice2=random.randint(1,6)
        diceSum=self.dice1+self.dice2
        if(diceSum==7):
            for player in self.players:
                player.sevenWasRolled()
            self.moveTheRobber(random.randint(0,3),random.randint(0,18))
        else:
            for player in self.players:
                player.yields(diceSum)
        self.updateScoreboard()
        self.alphaDice.destroy()
        self.betaDice.destroy()
        self.alphaDice=Button(self.window,image=self.diceImages[self.dice1-1],command=lambda: self.rollForTurn(),borderwidth=0)
        self.alphaDice.pack(side='left')
        self.betaDice=Button(self.window,image=self.diceImages[self.dice2-1],command=lambda: self.rollForTurn(),borderwidth=0)
        self.betaDice.pack(anchor=E,side='left')        
    def devRollForTurn(self):
        result=int(input("number 2-12 \n"))
        if(result>12 or result<2):
            print(result,"is not a valid result of rolling 2 6 sided dice.")
            return -1
        diceSum=result
        if(diceSum==7):
            for player in self.players:
                player.sevenWasRolled()
            self.moveTheRobber(random.randint(0,3),random.randint(0,18))
        else:
            for player in self.players:
                player.yields(diceSum)
        self.updateScoreboard()
        
    def moveTheRobber(self,playerMovingTheRobber,newPos):
        if(newPos<19 and newPos>-1):
            #Give the settlements adjacent to the hex on which the Robber was their yield back
            options=self.hexNum2SettlementNum[self.robberPos]
            for victim in options:#victim is the 1-indexed settlementNum,
                factor=0
                playerID=self.cityGrid[1][self.settlementNodes[0][victim-1][0]][self.settlementNodes[0][victim-1][1]]
                if(playerID>0):#If there is a settlement/city there,
                    factor+=1
                    if(playerID>4):#If it is a city
                        factor+=1
                    if(self.resourceTiles[self.robberPos][0]!=0):      #self.resourceTiles[product][0]==resource produced, self.resourceTiles[product][1]==roll required
                        self.players[(playerID-1)%4].yieldOnRoll[self.resourceTiles[self.robberPos][1]][self.resourceTiles[self.robberPos][0]-1]+=factor
            self.robberPos=newPos
            self.placeRobberToken()
            options=self.hexNum2SettlementNum[self.robberPos]
            #The robber has moved so now you are clear to reduce the yield of the settlements adjacent to it's new location.
            for victim in options:#victim is the 1-indexed settlementNum,
                factor=0
                playerID=self.cityGrid[1][self.settlementNodes[0][victim-1][0]][self.settlementNodes[0][victim-1][1]]
                if(playerID>0):#If there is a settlement/city there,
                    factor+=1
                    if(playerID>4):#If it is a city
                        factor+=1
                    if(self.resourceTiles[self.robberPos][0]!=0):      #self.resourceTiles[product][0]==resource produced, self.resourceTiles[product][1]==roll required
                        self.players[(playerID-1)%4].yieldOnRoll[self.resourceTiles[self.robberPos][1]][self.resourceTiles[self.robberPos][0]-1]-=factor
            #print("settlementNum options: ",options)
            #Handles stealing resources from the people next to the relocated robber.
            validTarget=[]
            for smt in options:
                spot=self.cityGrid[1][self.settlementNodes[0][smt-1][0]][self.settlementNodes[0][smt-1][1]]
                #print("settlement at given location is ",spot)
                if spot!=0 and spot!=playerMovingTheRobber and validTarget.count(spot)==0:
                    validTarget.extend([spot-1])
            #print(validTarget)
            if(len(validTarget)>0):
                self.robAfool(playerMovingTheRobber,validTarget[random.randint(0,len(validTarget)-1)])
            else:
                print("no valid victims to rob!")
        else:
            print("Invalid Location: Select a hex between 0 and 18")
    def placeRobberToken(self):
        self.canvas.delete(self.robTheRobber)
        self.robTheRobber=self.canvas.create_image(self.GRIDx+self.hexGridCoords[self.robberPos][0]+self.GRIDy-18,self.GRID+self.hexGridCoords[self.robberPos][1]+self.GRIDy-53,image=self.robberToken,anchor=NW);
    def robAfool(self,robberizer,robberizee):
        plunder=self.players[robberizee].robberized()
        #print("plunder is ",plunder)
        if(plunder>-1):
            self.players[robberizer].robberize(plunder)
        self.updateScoreboard()
        
    def updateScoreboard(self):
        self.player1Hand.destroy()
        self.player2Hand.destroy()
        self.player3Hand.destroy()
        self.player4Hand.destroy()
        self.player4Hand=Label(self.window,text=self.players[3].goFish())
        self.player4Hand.pack(side='right',anchor=N)
        self.player3Hand=Label(self.window,text=self.players[2].goFish())
        self.player3Hand.pack(side='right',anchor=NW)
        self.player2Hand=Label(self.window,text=self.players[1].goFish())
        self.player2Hand.pack(side='right',anchor=N)
        self.player1Hand=Label(self.window,text=self.players[0].goFish())
        self.player1Hand.pack(side='right',anchor=NE)
    def buildCity(self,settlementNum,playerID):
        if(settlementNum<0 or settlementNum>53):
            print("invalid settlement location")
            return -1
        elif(playerID>3 or playerID<0):
            print("invalid playerID")
            return -2
        elif( self.players[playerID].hand[1]<2 or self.players[playerID].hand[3]<3):#at least 1 brick, wheat, wool and lumber
            print("cannot afford a city!")
            return -3
        elif(settlementNum+1 in self.players[playerID].settlements):
            a,b=self.settlementNodes[0][settlementNum]
            self.cityGrid[1][a][b] += 4;
            x,y=self.settlementGridCoords[settlementNum]
            self.canvas.create_image(x+self.GRIDx-45,y+self.GRID-20,image=self.cities[playerID],anchor=NW)
            self.players[playerID].settlements.pop(self.players[playerID].settlements.index(settlementNum+1))#for tracking places to build cities later
            self.players[playerID].cities.append(settlementNum+1)#for tracking cities
            for product in self.settlementNodes[1][settlementNum]:    #product is a number 0-18 representing the resource tiles in self.resourceTiles[]
                if(self.resourceTiles[product][0]!=0 and self.robberPos!=product):      #self.resourceTiles[product][0]==resource produced, self.resourceTiles[product][1]==roll required
                    self.players[playerID].yieldOnRoll[self.resourceTiles[product][1]][self.resourceTiles[product][0]-1]+=1
            self.players[playerID].victoryPoints+=1
            self.players[playerID].hand[1]=self.players[playerID].hand[1]-2
            self.players[playerID].hand[3]=self.players[playerID].hand[3]-3
            print("player ",playerID+1," placed a city at ",settlementNum+1)
            self.updateScoreboard()
        else:
            print("Building a city requires an existing settlement!")
            return -4
        
    #|---NPC Script start---------------------------------------------------------------------------------------------------------------------------------------|
        
    def npcTurn(self,playerID):
        self.canPlayDevCard=True#You may only play 1 dev card per turn.
        self.npcPreRollSoldier(playerID)#Checks if it is possible and to your advantage to play a soldier before you roll and then does so when appropriate.
        self.rollForTurn
        #Consider trading with other players-
        #Consider using y
    def npcPreRollSoldier(self,playerID):#First, if your settlement has the robber on it and you have fewer than 7 cards in hand, move the robber to the optimal location
        if(self.players[playerID-1].developmentCardsBuilt[0]>0 and self.players[playerID-1].amBeingRobbed and self.players[playerID-1].handSize()<7):#You have a soldier and the robber might deny you resources and you have fewer than 7 cards in hand, so you want to move the robber before you roll.
            self.moveTheRobber(self.players[playerID-1],self.determineIdealRobberPos(playerID))
            self.canPlayDevCard=False
    def determineIdealRobberPos(self,playerID):#robberPos is 0-indexed 0-18, returns the optimal robberPos from the given player's perspective. Current implementation is level 1 complexity. see toChooseBestRobberPos.txt for the logic for levels 2 and 3
        bestLoc=0
        highestTally=-7#1 lower than the worst possible
        for i in range(0,18):
            tally=0;
            options=self.hexNum2SettlementNum[i]
            for victim in options:#victim is the 1-indexed settlementNum,
                factor=0
                victimID=self.cityGrid[1][self.settlementNodes[0][victim-1][0]][self.settlementNodes[0][victim-1][1]]
                if(victimID>0):#If there is a settlement/city there,
                    factor+=1
                    if(victimID>4):#If it is a city
                        factor+=1
                if(victimID==playerID or victimID==playerID+4):
                    tally-=factor
                else:
                    tally+=factor
            if(tally>highestTally):
                bestLoc=i
                highestTally=tally
        return bestLoc
        #return random.randint(0,18)
    def determineBestSettlementPos(self):#returns the highest yielding settlementNum 0-indexed
        plentitude={2:1,3:2,4:3,5:4,6:5,8:5,9:4,10:3,11:2,12:1}
        bestLoc=0
        bestYPT=0
        for i in range(0,53):
            ypt=0
            a,b=self.settlementNum2ColRow[i]
            if(self.verifySettlementLegality(a,b)==True):
                for yieldingHex in self.settlementNodes[1][i]:
                    if(self.resourceTiles[yieldingHex][0]>0):#not a desert,
                        ypt+=plentitude[self.resourceTiles[yieldingHex][1]]
                if(self.settlementNodes[3][i]>0):#check for harbors
                    ypt+=0.5#A harbor is worth half a resource per turn(?)
            if(ypt>bestYPT):
                bestYPT=ypt
                bestLoc=i
        print("highest yield per turn ",bestYPT)
        return bestLoc
    def determineBestSettlementPosLvl2(self,playerID):#returns the highest value yielding settlementNum 0-indexed from the perspective of the input player; Level 2 places a premium on diversifying the resources available to you. (wheat>ore>brick>lumber>wool)
        resourceIndex={0:"Brick",1:"Wheat",2:"Wool",3:"Ore",4:"Lumber"}
        currentResourceYield=self.players[playerID].yieldSummary()
        #print("cur yield:",currentResourceYield)
        plentitude={2:1,3:2,4:3,5:4,6:5,8:5,9:4,10:3,11:2,12:1}
        #resValue={0:, 1:, 2:, 3:, 4:} #brick wheat wool ore lumber
        resAbundance={0:1.33, 1:1, 2:1.33, 3:1.33, 4:1}
        resValueWhenScarce={0:1.03, 1:1.05, 2:1.01, 3:1.04, 4:1.02} #if you have no access to it, player.yieldsonroll[resource]==0, than it's worth: extra
        bestLoc=0
        bestYPT=0
        yieldDiversityOfBest=[]#list of the token of tiles resources are pulled from, bigger len is better
        resourcePriorityFactorSumOfBest=0#sum of the marginal scarcity of a given resource for the current player
        for i in range(0,53):
            ypt=float(0)
            yieldDiversity=[]
            resourcePriorityFactor=0
            a,b=self.settlementNum2ColRow[i]
            if(self.verifySettlementLegality(a,b)==True):
                for yieldingHex in self.settlementNodes[1][i]:
                    resource,token=self.resourceTiles[yieldingHex]
                    if(resource>0):#not a desert,
                        if(currentResourceYield[resource-1]==0):#if you don't have that resource yet, factor the order of resource priorities into your evaluation
                            #print(resourceIndex[resource-1],"has value of",float(plentitude[token]*resValueWhenScarce[resource-1]))
                            ypt+=float(plentitude[token])#1-5 value of the token * resourceScarcityValueAdjustment
                            resourcePriorityFactor+=resValueWhenScarce[resource-1]
                            if(token not in yieldDiversity):
                                yieldDiversity.append(token)
                        else:
                            ypt+=float(plentitude[token])#1-5 value of the token +0.001 to favor an 8 node which pulls from 3 resources over an 8 node which pulls from 2 resources, but not over an 8 which has a harbor.
                            if(token not in yieldDiversity):
                                yieldDiversity.append(token)
                if(self.settlementNodes[3][i]>0):#check for harbors
                    ypt+=0.5#A harbor is worth half a resource per turn(?)
            if(ypt>bestYPT):
                bestYPT=ypt
                bestLoc=i
                yieldDiversityOfBest=yieldDiversity
                resourcePriorityFactorSumOfBest=resourcePriorityFactor
            if(ypt==bestYPT):#If the net yield is the same, consider the diversity of the yielding rolls and the desirability of the resources yielded to select the superior location
                if(resourcePriorityFactor+len(yieldDiversity)>len(yieldDiversityOfBest)+resourcePriorityFactorSumOfBest):
                    if(len(yieldDiversityOfBest)+resourcePriorityFactorSumOfBest>0):
                        print("chose",i+1,"over",bestLoc+1," on a margin of",resourcePriorityFactor+len(yieldDiversity)-len(yieldDiversityOfBest)-resourcePriorityFactorSumOfBest)
                    bestYPT=ypt
                    bestLoc=i
                    yieldDiversityOfBest=yieldDiversity
                    resourcePriorityFactorSumOfBest=resourcePriorityFactor
        print("highest yield per turn ",bestYPT)
        return bestLoc
    def npcOffer(self,offer):
        return False
    def npcConsider(self,offer):
        return False
    def endTurn(self,playerID):
        self.players[playerID-1].developmentCardsBuilt+=self.players[playerID-1].developmentCardsBuiltThisTurn #transfers dev cards built this turn over to your playable dev cards for use in later turns.
        self.players[playerID-1].developmentCardsBuiltThisTurn=[0,0,0,0,0] #empties out your tray of dev cards that you built this turn and cannot play until at least 1 turn cycle has passed.
    #|---NPC Script end---------------------------------------------------------------------------------------------------------------------------------------|
    
    #def offTheMarket(self,thingNums,roadOrSettlement):#something has just been placed on the board. It must now be removed from every player's canBuild
    #    for playerID in self.players:
    #        self.players[playerID].updateBuildableReg(thingNums,roadOrSettlement,playerID)
    def placeSettlement(self,col,row,playerID): #col,row are in the 1-6,a-k format
        #Implementation(?): after the start of the game, Players keep track of where they can and cannot attempt to build. Every time a piece is placed onto the map these tables are adjusted accordingly.
        #convert 1-6,a-k to (0-53) to utilize the self.settlementNodes[0] and [1] lookup charts.
        settlementNum=self.sNCC[col-1][row-1]-1
        a,b=self.settlementNodes[0][settlementNum]
        #print(settlementNum)
        #Handle the addition of the harbor to the player's harbor reg
        if(settlementNum==-1):
            print("invalid settlement location")
            return -1
        #check for a settlement within 1 tile of the target location
        if(self.verifySettlementLegality(col,row)==False):
            print("{} is too close to another settlement!".format(settlementNum))
            return -2
        if(self.settlementNodes[3][settlementNum]>0):#if a harbor is present
            self.players[playerID].harbors[self.harborGridCoords[self.settlementNodes[3][settlementNum]-1][3]]=1;
        #update the cityGrid[1] grid with the playerID (1+playerID=1-4)
        self.cityGrid[1][a][b] = 1+playerID;
        #place the settlement onto the board visually
        x,y=self.settlementGridCoords[settlementNum]
        self.canvas.create_image(x+self.GRIDx-30,y+self.GRID-20,image=self.houses[playerID],anchor=NW)
        self.players[playerID].settlements.append(settlementNum+1)#for tracking places to build cities later
        #self.offTheMarket(settlementNum,True)#removes this particular settlement node and all directly adjacent nodes from the players' build registries
        for product in self.settlementNodes[1][settlementNum]:    #product is a number 0-18 representing the resource tiles in self.resourceTiles[]
            if(self.resourceTiles[product][0]!=0 and self.robberPos!=product):      #self.resourceTiles[product][0]==resource produced, self.resourceTiles[product][1]==roll required
                self.players[playerID].yieldOnRoll[self.resourceTiles[product][1]][self.resourceTiles[product][0]-1]+=1
        self.settlementUpdateCanBuild(settlementNum+1,playerID)
        self.players[playerID].victoryPoints+=1
        
    def settlementUpdateCanBuild(self,obNum,playerID):#a player has just placed a settlement. This blocks opposing roads that end on this node from building past it, other settlements from being built on nodes 1 unit away or on the same node
        print("player ",playerID+1," placed a settlement at ",obNum)
        for i in range(0,len(self.players)):
            if i==playerID:#This player just placed their settlement. They can now build roads shooting off from it and can no longer build a settlement at this location.
                #self.showMap()
                for road in self.settlementNodes[2][obNum-1]:
                    #print("road: ",road)
                    if(self.players[i].canBuild[1].count(road)==0 and self.roadGrid[road-1]==0):#If its not present and hasn't been built yet, add it
                        self.players[i].canBuild[1].append(road)
                        self.players[i].canBuild[1].sort
                if (self.players[i].canBuild[0].count(obNum)>0):
                    self.players[i].canBuild[0].pop(self.players[i].canBuild[0].index(obNum))##remove the road you just built from your list of valid places to build a road
            else:#Another player has just placed a settlement. Check canBuild[1] for that settlementNum and remove it if it is present.
                if (self.players[i].canBuild[0].count(obNum)>0):
                    self.players[i].canBuild[0].pop(self.players[i].canBuild[0].index(obNum))
                for potentiallyBlockedRoad in self.settlementNodes[2][obNum-1]:#for every road adjacent to the newly placed settlement,
                    #print("potentially blocked road: ",potentiallyBlockedRoad)
                    alternativeConnection=True
                    if(self.players[i].canBuild[1].count(potentiallyBlockedRoad)>0):
                        for potentiallyConnectingRoad in self.roadConnections[0][potentiallyBlockedRoad-1]:#for every road connected to this road adjacent to the newly placed settlement present in this other player's canBuild,
                            if(self.players[i].roads.count(potentiallyConnectingRoad)>0 and potentiallyConnectingRoad!=potentiallyBlockedRoad):#If this player has an unblocked road connected to this settlment,
                                alternativeConnection=False#don't remove it from canBuild as it is not blocked to this player.
                        if(alternativeConnection):#True when not present, False when present
                            self.players[i].canBuild[1].pop(self.players[i].canBuild[1].index(potentiallyBlockedRoad))
            #print("nodes: ",self.players[i].canBuild[0])
            sN=0
            while (sN<len(self.players[i].canBuild[0])):
                #print(self.vSL(self.players[i].canBuild[0][sN])," for ", self.players[i].canBuild[0][sN])
                if(self.vSL(self.players[i].canBuild[0][sN]==False)):
                    #print("removing ",self.players[i].canBuild[0][sN],"from ",self.players[i].canBuild)
                    self.players[i].canBuild[0].pop(sN)
                else:
                    sN+=1
            #countOfSettlements=0
            #for settlementNode in self.players[i].canBuild[0]:#a player has just built a settlement, check your canBuild[0] list for settlements that are no longer legal placements and pop them.
            #    print(self.vSL(settlementNode)," for ", settlementNode)
            #    if(self.vSL(settlementNode)==False):
            #        print("removing ",self.players[i].canBuild[0][countOfSettlements],"from ",self.players[i].canBuild)
            #        self.players[i].canBuild[0].pop(countOfSettlements)
            #    countOfSettlements+=1 
            self.players[i].canBuild[0].sort()
            self.players[i].canBuild[1].sort()
            print(self.players[i].canBuild)
            
    def buySettlement(self,col,row,playerID):#player must have the resources to pay for it
        #convert 1-6,a-k to (0-53) to utilize the self.settlementNodes[0] and [1] lookup charts.
        settlementNum=self.sNCC[col-1][row-1] #This method is checking the 1-indexed value, not the 0-indexed value. This value is not passed out of the function.
        print("valid locations: ",self.players[playerID].canBuild[0]," yet you chose: ",settlementNum)
        if(self.players[playerID].hand[0]==0 or self.players[playerID].hand[1]==0 or self.players[playerID].hand[2]==0 or self.players[playerID].hand[4]==0):#at least 1 brick, wheat, wool and lumber
            print("cannot afford a settlement!")
            return -1
        elif(self.players[playerID].canBuild[0].count(settlementNum)==0):#self.players[playerID].canBuildHere[settlementNum]
            print("Location Invalid")
            return -2
        else:
            self.players[playerID].hand[0]=self.players[playerID].hand[0]-1
            self.players[playerID].hand[1]=self.players[playerID].hand[1]-1
            self.players[playerID].hand[2]=self.players[playerID].hand[2]-1
            self.players[playerID].hand[4]=self.players[playerID].hand[4]-1
            self.placeSettlement(col,row,playerID)
            self.updateScoreboard()
        
    def verifySettlementLegality(self,col,row):
        #check for a prexisting settlement within 1 tile of the target on the current simulation's cityGrid
        settlementNum=self.sNCC[col-1][row-1]-1
        a,b=self.settlementNodes[0][settlementNum]
        safe=[0,0,0,0]#left, right, up and down
        if(a>0):
            safe[0]=1;
        if(a<10):
            safe[1]=1;
        if(b>0):
            safe[2]=1;
        if(b<10):
            safe[3]=1;
        #print("{}, {}, {}".format(a,b,safe))
        for i in range(0-safe[0],1+safe[1]):
            for j in range(0-safe[2],1+safe[3]):
                if(self.cityGrid[1][a+i][b+j]!=0):
                    return False
        return True
    def vSL(self,settlementNum):#internally zero indexes
        #check for a prexisting settlement within 1 tile of the target on the current simulation's cityGrid
        a,b=self.settlementNodes[0][settlementNum-1]
        safe=[0,0,0,0]#left, right, up and down
        if(a>0):
            safe[0]=1;
        if(a<10):
            safe[1]=1;
        if(b>0):
            safe[2]=1;
        if(b<10):
            safe[3]=1;
        #print("{}, {}, {}".format(a,b,safe))
        for i in range(0-safe[0],1+safe[1]):
            for j in range(0-safe[2],1+safe[3]):
                if(self.cityGrid[1][a+i][b+j]!=0):
                    return False
        return True

    def roadUpdateCanBuild(self,obNum,playerID):
        print("player ",playerID+1," placed a road at ",obNum)
        #self.showRoad()
        for i in range(0,len(self.players)):
            if i==playerID:#This player has just placed a road. Each connected road location must be checked for existing roads, if empty, append them to canBuild[1] Next check the legality of the settlement nodes connected to this road and append them to [0] if they are legal. Remove this road from [1]
                endOfTheRoad=False#This is set to True if an enemy settlement/city is present in either of the settlementNodes connected to the newly built road (the node behind could never be occupied by an enemy node as that would have prevented the construction of this road.)
                for node in self.roadConnections[1][obNum-1]:#Now check the settlementNodes touched by the new road
                    #print(self.cityGrid[1][self.settlementNodes[0][node][0]-1][self.settlementNodes[0][node][1]-1]," > 0 , ",self.settlementNodes[0][node][0]-1,", ",self.settlementNodes[0][node][1]-1)
                    #print("node =",node)
                    #print(self.settlementNodes[0][node-1][0]-1,self.settlementNodes[0][node-1][1]-1)
                    if(self.cityGrid[1][self.settlementNodes[0][node-1][0]-1][self.settlementNodes[0][node-1][1]-1]>0 and self.cityGrid[1][self.settlementNodes[0][node-1][0]-1][self.settlementNodes[0][node-1][1]-1] != playerID+1):
                        endOfTheRoad=True
                    if(self.players[i].canBuild[0].count(node)==0 and self.vSL(node)):#if not present and it's legal, add it.
                        self.players[i].canBuild[0].append(node)
                        self.players[i].canBuild[0].sort
                if(endOfTheRoad==False):#You cannot build past an enemy settlement, thus only add new roads to canBuild if no enemy settlements were adjacent to the newly constructed road.
                    for road in self.roadConnections[0][obNum-1]:
                        if(self.players[i].canBuild[1].count(road)==0 and self.players[i].roads.count(road)==0 and self.roadGrid[road-1]==0):#If its not present and the location is empty, add it
                            self.players[i].canBuild[1].append(road)
                            self.players[i].canBuild[1].sort
                if (self.players[i].canBuild[1].count(obNum)>0):
                    self.players[i].canBuild[1].pop(self.players[i].canBuild[1].index(obNum))##remove the road you just built from your list of valid places to build a road
            else:#Another player has just placed a road. Check canBuild[1] for that roadNum and remove it if it is present.
                if (self.players[i].canBuild[1].count(obNum)>0):
                    self.players[i].canBuild[1].pop(self.players[i].canBuild[1].index(obNum))
            #print("before sort: ",self.players[i].canBuild)
            self.players[i].canBuild[0].sort()
            self.players[i].canBuild[1].sort()
            #print(self.players[i].canBuild)
        print(self.players[0].canBuild)
    def placeRoad(self,col,row,playerID):#col=1-11,row=1-10
        #first check that the player has a brick and a lumber in hand
        #second, check that they have a place to build the road out to (cannot place roads where a road already exists: [1-3,0]; can only place roads adjacent to your own existing roads;
        roadNum=self.colRow2RoadNum[col-1][row-1]-1
        if(roadNum==-1):
            print("invalid road location")
            return -1
        elif(self.roadGrid[roadNum]>0):
            print("A pre-existing road is blocking the construction of a new road at this location!")
            return -2
        #print("roadNum = ",roadNum)
        x=self.roadGridCoords[roadNum][0]
        y=self.roadGridCoords[roadNum][1]
        self.canvas.create_image(x,y,image=self.roads[playerID][self.roadGridCoords[roadNum][2]],anchor=NW)
        self.roadGrid[roadNum]=playerID+1;
        self.redrawAdjacentSettlementOrCity(roadNum)
        self.players[playerID].roads.append(roadNum)
        self.roadUpdateCanBuild(roadNum+1,playerID)
        #check for longest road and distribute victory points accordingly.
    def buyRoad(self,col,row,playerID):#player must have the resources to pay for it
        roadNum=self.colRow2RoadNum[col-1][row-1] #This method is checking the 1-indexed value, not the 0-indexed value. This value is not passed out of the function.
        #print("valid locations: ",self.players[playerID].canBuild[1]," yet you chose: ",roadNum)
        if(self.players[playerID].hand[0]==0 or self.players[playerID].hand[4]==0):#at least 1 brick and lumber
            print("cannot afford a road!")
            return -1
        elif(self.players[playerID].canBuild[1].count(roadNum)==0):
            print("Location Invalid")
            return -2
        else:
            self.players[playerID].hand[0]=self.players[playerID].hand[0]-1
            self.players[playerID].hand[4]=self.players[playerID].hand[4]-1
            self.updateScoreboard()
            self.placeRoad(col,row,playerID)
    
    def redrawAdjacentSettlementOrCity(self,roadNum):
        for settlementNum in self.roadConnections[1][roadNum]:#pulls the 1-indexed settlementNums the road connects to
            #print("settlementNum to be checked: ",settlementNum)
            for player in self.players:
                #print(player.name," settlements: ",player.settlements)
                for settlement in player.settlements:
                    #print("settlementNum = ",settlement)
                    if(settlement==settlementNum):
                        #print("it exists")
                        x,y=self.settlementGridCoords[settlementNum-1]
                        self.canvas.create_image(x+self.GRIDx-30,y+self.GRID-20,image=self.houses[int(player.name)-1],anchor=NW)
                for city in player.cities:
                    print("city",city,"settlementNum",settlementNum)
                    if(city==settlementNum):
                        x,y=self.settlementGridCoords[settlementNum-1]
                        self.canvas.create_image(x+self.GRIDx-45,y+self.GRID-20,image=self.cities[int(player.name)-1],anchor=NW)
    def buyADevelopmentCard(self,playerID):#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        if(playerID<0 or playerID>3):
            print("invalid playerID, value between 0 and 3 expected")
            return -1
        elif(self.players[playerID].hand[1]<1 or self.players[playerID].hand[2]<1 or self.players[playerID].hand[3]<1):
            print("Player",playerID,"cannot afford a settlement card.")
            return -2
        else:
            self.players[playerID].hand[1]=self.players[playerID].hand[1]-1
            self.players[playerID].hand[2]=self.players[playerID].hand[2]-1
            self.players[playerID].hand[3]=self.players[playerID].hand[3]-1
            self.drawADevelopmentCard(playerID)
            print(playerID,"has drawn a development card")
    def drawADevelopmentCard(self,playerID):#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        card=self.developmentCardTable.pullADrop()
        self.players[playerID].developmentCardsBuilt[card]=self.players[playerID].developmentCardsBuilt[card]+1
        self.updateScoreboard()
    def playADevelopmentCard(self,playerID,card):#0=soldier,1=vp,2=monopoly,3=road building,4=year of plenty
        if(self.players[playerID].developmentCardsBuilt[card]>0):
            self.players[playerID].developmentCardsBuilt[card]=self.players[playerID].developmentCardsBuilt[card]-1
            self.players[playerID].developmentCardsPlayed[card]=self.players[playerID].developmentCardsPlayed[card]+1
            if(card==0):#soldier
                self.moveTheRobber(playerID,int(input("Where would you like us to march this scoundrel to, governor? Select a hex 0-18 counting by collumn then by row. \n")))
                if(self.players[playerID].developmentCardsPlayed[0]>self.largestArmy[0]):
                    if(self.largestArmy[0]>2):#if someone has taken it before, then remove their points,
                        self.players[self.largestArmy[1]].victoryPoints-=2
                    self.largestArmy[0]+=1
                    self.largestArmy[1]=playerID
                    self.players[playerID].victoryPoints+=2
            if(card==1):#victory point
                self.players[playerID].victoryPoints+=1
            if(card==2):#monopoly
                summ=0
                resource=int(input("You greedy dog! You've stolen it all for yourself, but what did you steal? 0 is bricks, 1 is wheat, 2 is wool, 3 is ore and 4 is lumber."))
                #I should probably add a loop to keep trying this until they input a valid number 0-4, but also, if they mess that up its on them for wasting the monopoly.
                for player in self.players:
                    if(player!=playerID):
                        summ+=player.hand[resource]
                        player.hand[resource]=0
                self.players[playerID].hand[resource]+=summ
                print("Player",playerID,"has greedily stolen",summ,self.resourceIndex[resource],"from the other players!")
            if(card==3):#road building!
                #firstRoad=int(input("Immigration has given us the opportunity to build 2 roads on the cheap- where do you wish us to put them to work, governor? 0-71, count up from the top left collumns by rows."))
                #secondRoad=int(input("Immigration has given us the opportunity to build 2 roads on the cheap- where do you wish us to put them to work, governor? 0-71, count up from the top left collumns by rows."))
                options=[]
                for roadLoc in self.players[playerID].canBuild[1]:
                    options.append(roadLoc)
                optStr=' '.join(str(word) for word in options)
                optString="Immigration has given us the opportunity to build 2 roads on the cheap- where do you wish us to put them to work, governor? Valid locations are:",optStr
                firstRoad=int(input(optString))
                a,b=self.roadNum2ColRow[firstRoad-1]
                self.placeRoad(a,b,playerID)
                options=[]
                for roadLoc in self.players[playerID].canBuild[1]:
                    options.append(roadLoc)
                optStr=' '.join(str(word) for word in options)
                optString="Immigration has given us the opportunity to build 2 roads on the cheap- where do you wish us to put them to work, governor? Valid locations are:",optStr
                secondRoad=int(input(optString))
                a,b=self.roadNum2ColRow[secondRoad-1]
                self.placeRoad(a,b,playerID)
            if(card==4):#year of plenty!
                for i in range(0,2):
                    imp="Select card #",i+1,"0 is bricks, 1 is wheat, 2 is wool, 3 is ore and 4 is lumber."
                    whatchaWant=int(input(imp))
                    self.players[playerID].hand[whatchaWant]=self.players[playerID].hand[whatchaWant]+1
            self.updateScoreboard()
                    
    def showMap(self):
        print("SettlementMap");
        for line in self.cityGrid[1]:
            print(line);
        #print("ResourceTiles");
        #i=0;
        #for tile in self.resourceTiles:
        #    if(i==self.robberPos):
        #        print(str(tile) + " robber");
        #    else:
        #        print(tile);
        #    i+=1;
    def showRoad(self):
        print("RoadGrid");
        print(self.roadGrid)
    def fillMap(self):
        for node in simulation_1.settlementGridCoords:
            coin=random.randint(0,1)
            if(coin==1):
                simulation_1.canvas.create_image(node[0]+simulation_1.GRIDx-30,node[1]+simulation_1.GRID-20,image=simulation_1.houses[random.randint(0,3)],anchor=NW)
            else:
                simulation_1.canvas.create_image(node[0]+simulation_1.GRIDx-45,node[1]+simulation_1.GRID-20,image=simulation_1.cities[random.randint(0,3)],anchor=NW)
    def trueFillMap(self):
        for i in range(1,11):
            for j in range(1,12):
                #print("{}, {}".format(j,i))
                self.placeRoad(j,i,0)
        for i in range(1,12):
            for j in range(1,7):
                self.placeSettlement(j,i,0)
    def buyItAll(self):
        self.players[0].hand=[999,999,999,999,999]
        self.placeRoad(1,3,0)
        self.placeSettlement(3,4,3);
        self.placeSettlement(2,6,2);
        self.placeSettlement(5,5,1);
        for a in range(1,13):
            for b in range(1,12):
                try:
                    self.buyRoad(a,b,0)
                except IndexError as c:
                    print(c,"occured")

simulation_1 = simulation();
#simulation_1.buyItAll()
#simulation_1.buySettlement(3,7,0);
#simulation_1.buyRoad(3,7,0);
#simulation_1.players[0].hand=[200,2,2,0,200]
#simulation_1.buySettlement(3,7,0);
#simulation_1.buyRoad(3,7,0);
#simulation_1.placeRoad(9,7,0)
#simulation_1.buyRoad(9,8,0)
#simulation_1.buyRoad(9,9,0)
#simulation_1.buyRoad(10,4,0)
#simulation_1.buyRoad(10,5,0)
#simulation_1.buyRoad(11,7,0)
#simulation_1.buyRoad(11,8,0)
if(False):#Npc def testing, mocks a 4 bot game.
    for i in range(0,4):
        bestLoc=simulation_1.determineBestSettlementPos()#0-indexed
        a,b=simulation_1.settlementNum2ColRow[bestLoc]
        print("best location",bestLoc+1," a",a," b",b)
        simulation_1.placeSettlement(a,b,i)
        roadNum=simulation_1.players[i].canBuild[1][random.randint(0,len(simulation_1.players[i].canBuild[1])-1)]-1
        c,d=simulation_1.roadNum2ColRow[roadNum]
        simulation_1.placeRoad(c,d,i)
    for i in range(0,4):
        bestLoc=simulation_1.determineBestSettlementPos()#0-indexed
        a,b=simulation_1.settlementNum2ColRow[bestLoc]
        print("best location",bestLoc+1," a",a," b",b)
        simulation_1.placeSettlement(a,b,3-i)
if(True):#Npc def testing, mocks a 4 bot game using lvl2 best settlement assessment logic.
    for i in range(0,4):    #First Settlements and roads,
        bestLoc=simulation_1.determineBestSettlementPosLvl2(i)#0-indexed
        a,b=simulation_1.settlementNum2ColRow[bestLoc]
        print("best location",bestLoc+1," a",a," b",b)
        simulation_1.placeSettlement(a,b,i)
        roadNum=simulation_1.players[i].canBuild[1][random.randint(0,len(simulation_1.players[i].canBuild[1])-1)]-1 #Selects a road to build from among this player's legal options.
        c,d=simulation_1.roadNum2ColRow[roadNum]
        simulation_1.placeRoad(c,d,i)
    for i in range(0,4):    #Second Settlements and roads
        bestLoc=simulation_1.determineBestSettlementPosLvl2(i)#0-indexed
        a,b=simulation_1.settlementNum2ColRow[bestLoc]
        print("best location",bestLoc+1," a",a," b",b)
        simulation_1.placeSettlement(a,b,3-i)
        for resource in simulation_1.settlementNodes[1][bestLoc]:  #bestows the resources yielded by the hexes adjacent to the second settlements
            simulation_1.players[3-i].hand[simulation_1.resourceTiles[resource][0]-1]+=1
        roadNum=simulation_1.settlementNodes[2][bestLoc][random.randint(0,len(simulation_1.settlementNodes[2][bestLoc])-1)]-1 #selects a road to build from among the roads connected to the settlement that was just placed.
        c,d=simulation_1.roadNum2ColRow[roadNum]
        simulation_1.placeRoad(c,d,3-i)
        simulation_1.updateScoreboard()
if(False):#test level placeBestSettlementlvl2 one a smaller sample size
    i=0
    bestLoc=simulation_1.determineBestSettlementPosLvl2(i)#0-indexed
    a,b=simulation_1.settlementNum2ColRow[bestLoc]
    print("best location",bestLoc+1," a",a," b",b)
    simulation_1.placeSettlement(a,b,i)
    print(simulation_1.players[i].yieldSummary())
    bestLoc=simulation_1.determineBestSettlementPosLvl2(i)#0-indexed
    a,b=simulation_1.settlementNum2ColRow[bestLoc]
    print("best location",bestLoc+1," a",a," b",b)
    simulation_1.placeSettlement(a,b,i)
if(False):#Tests harbors and trading with the bank for resources, implemented at the player class level.
    simulation_1.players[0].hand=[40,0,0,0,4]
    simulation_1.players[0].canAfford("settlement")
if(False):#Tests harbors and trading with the bank for resources, implemented at the player class level.
    simulation_1.players[0].hand=[10,0,0,0,0]
    simulation_1.players[0].useBankOrPorts(4,0)
    print(simulation_1.players[0].hand)
    simulation_1.players[0].useBankOrPorts(0,4)
    print(simulation_1.players[0].hand)
    simulation_1.players[0].harbors[0]=1
    simulation_1.players[0].useBankOrPorts(0,4)
    print(simulation_1.players[0].hand)
    simulation_1.players[0].harbors[1]=1
    simulation_1.players[0].useBankOrPorts(0,4)
    print(simulation_1.players[0].hand)

#simulation_1.buyRoad(5,6,0)
#simulation_1.buySettlement(3,7,0);
if(False):
    simulation_1.moveTheRobber(1,4)
    simulation_1.placeSettlement(3,7,0);
    simulation_1.moveTheRobber(1,10)
    simulation_1.placeSettlement(4,9,0);
    simulation_1.moveTheRobber(1,1)
    simulation_1.buildCity(35,0);
    simulation_1.players[0].hand=[0,2,0,3,0]
    simulation_1.updateScoreboard()
    simulation_1.buildCity(35,0);
    simulation_1.placeRoad(6,5,0)
    simulation_1.placeSettlement(2,5,3);
    simulation_1.placeSettlement(5,5,3);
    simulation_1.placeSettlement(2,7,1);
    simulation_1.placeSettlement(5,7,1);
    simulation_1.placeSettlement(3,5,2);
    simulation_1.placeSettlement(4,3,2);
if(False):
    for i in range(0,25):
        simulation_1.drawADevelopmentCard(0)
    for i in range(0,5):
        simulation_1.playADevelopmentCard(0,i)
#simulation_1.moveTheRobber(1,3)
#simulation_1.moveTheRobber(4,0)
#simulation_1.showMap();
#simulation_1.fillMap()
#simulation_1.canvas.create_image(4*simulation_1.GRIDx-6,2*simulation_1.GRID+6,image=simulation_1.roads[3][2],anchor=NW)
#simulation_1.canvas.create_image(4*simulation_1.GRIDx-6,2.5*simulation_1.GRID+6,image=simulation_1.roads[3][1],anchor=NW)
#simulation_1.canvas.create_image(3*simulation_1.GRIDx+59,simulation_1.GRID-6,image=simulation_1.roads[3][0],anchor=NW)
#simulation_1.placeSettlement(1,4,0);
#simulation_1.placeSettlement(3,4,0);
#simulation_1.trueFillMap()
#simulation_1.placeRoad(11,8,0)
#simulation_1.placeRoad(4,10,0)
#simulation_1.placeSettlement(2,3,0);
#simulation_1.placeSettlement(1,1,0);
#simulation_1.showMap();
#simulation_1.players[1].hand=[10,0,0,0,4]
#print(simulation_1.players[1].hand)
#simulation_1.players[1].harbors=[0,0,0,0,0,0]
#simulation_1.players[1].useBankOrPorts(4,0)
#print(simulation_1.players[1].hand)
#print(simulation_1.players[0].harbors)

