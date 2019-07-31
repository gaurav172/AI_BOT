import sys
import random
import time
from copy import deepcopy

class Team15():

    def __init__(self):
        self.available_moves = []
        self.BoardHeuristics = {}
        self.BlockHeuristics = {}
        self.BoardHash = [long(0), long(0)]
        self.BlockHash = [[[long(0) for i in range(3)] for j in range(3) ] for k in range(2)]
        self.RandTable = [[[[long(0) for p in range(2)] for i in range(9)] for j in range(9) ] for k in range(2)]
        self.tle = 0
        self.Me = 'o'
        self.INF = 1e14
        self.ct = 0
        self.curr = '0'
        self.oldm = [0, 0, 0]
        self.SmallValue = [[[long(0) for k in xrange(3)] for j in xrange(3)] for i in xrange(2)]
        self.Smallboard_weight = [ [4, 6, 4] , [6, 3, 6] ,[4, 6, 4] ]
        self.Drawfactor = 50
        for k in range(2):
            for i in range(9):
                for j in range(9):
                    for p in range(2):
                        self.RandTable[k][i][j][p] = long(random.randint(1,2**64))


    def opponent(self,flag):
        if flag == 'x':
            return 'o'
        return 'x'

    def CalScoreifDraw(self,board):
        score = 0
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    if board.small_boards_status[k][i][j] == self.Me:
                        score  = score + self.Smallboard_weight[i][j]
        
        return score*self.Drawfactor

    def addmove(self,move,flag):
        if flag == 'o':
            self.BoardHash[move[0]]^=self.RandTable[move[0]][move[1]][move[2]][0]
            self.BlockHash[move[0]][move[1]/3][move[2]/3]^=self.RandTable[move[0]][move[1]][move[2]][0]
        if flag == 'x':
            self.BoardHash[move[0]]^=self.RandTable[move[0]][move[1]][move[2]][1]
            self.BlockHash[move[0]][move[1]/3][move[2]/3]^=self.RandTable[move[0]][move[1]][move[2]][1]
            

    def value(self,mat,flag):
        ans = 0
        for i in range(3):
            won = 0
            unmarked = 0
            for j in range(3):
                if mat[i][j] == flag:
                    won = won + 1
                if mat[i][j] == '-':
                    unmarked = unmarked + 1
            if won + unmarked == 3:
                if won == 2:
                    ans = ans + 30000
                if won == 1:
                    ans = ans + 700
        for j in range(3):
            won = 0
            unmarked = 0
            for i in range(3):
                if mat[i][j] == flag:
                    won = won + 1
                if mat[i][j] == '-':
                    unmarked = unmarked + 1
            if won + unmarked == 3:
                if won == 2:
                    ans = ans + 30000
                if won == 1:
                    ans = ans + 700

        won = 0
        unmarked = 0
        for i in range(3):
            if mat[i][i] == flag:
                won = won + 1
            if mat[i][i] == '-':
                unmarked = unmarked + 1
        
        if won + unmarked == 3:
            if  won == 2:
                ans = ans + 30000
            if  won == 1:
                ans = ans + 700

        won = 0
        unmarked = 0
        for i in range(3):
            if mat[i][2-i] == flag:
                won = won + 1
            if mat[i][2-i] == '-':
                unmarked = unmarked + 1
        
        if won + unmarked == 3:
            if  won == 2:
                ans = ans + 30000
            if  won == 1:
                ans = ans + 700
        
        return ans
    
    def compute_block(self,board,flag):
        for k in range(2):
            for i in range(3):
                for j in range(3):
                    self.SmallValue[k][i][j]=0
                    if board.small_boards_status[k][i][j] == flag:
                        self.SmallValue[k][i][j] = 500000
                    if board.small_boards_status[k][i][j] != '-':
                        continue
                    mat = [[long(0) for p in range(3)] for q in range(3)]
                    x = 3*i
                    y = 3*j
                    for a in range (3):
                        for b in range(3):
                            mat[a][b] = board.big_boards_status[k][x+a][y+b]
                    if (self.BlockHash[k][i][j],flag) in self.BlockHeuristics:
                        self.SmallValue[k][i][j] = self.BlockHeuristics[(self.BlockHash[k][i][j],flag)]
                    else :
                        self.SmallValue[k][i][j] = self.value(mat,flag)
                        self.BlockHeuristics[(self.BlockHash[k][i][j],flag)] = self.SmallValue[k][i][j]
                    # if k == 0 and i == 0 and j == 0 and mat[0][0] == 'x':
                        # print(self.SmallValue[k][i][j])
                        # if mat[0][2] == 'o' :
                            # print("wrong move",self.SmallValue[k][i][j])
                        # if mat[1][1] == 'o' :
                            # print("write move",self.SmallValue[k][i][j])

    def val_big(self,board,k,flag):
        if (self.BoardHash[k],flag) in self.BoardHeuristics:
            return self.BoardHeuristics[(self.BoardHash[k],flag)]
        ans = 0
        for i in range(3):
            for j in range(3):
                if board.small_boards_status[k][i][j] == flag:
                    ans = ans + 20*self.SmallValue[k][i][j]
                if board.small_boards_status[k][i][j] == '-':
                    ans = ans + self.SmallValue[k][i][j]

        for i in range(3):
            won = 0
            unmarked = 0
            sval = 0
            for j in range(3):
                if board.small_boards_status[k][i][j] == flag:
                    won = won + 1
                if board.small_boards_status[k][i][j] == '-':
                    unmarked = unmarked + 1
                sval = sval + self.SmallValue[k][i][j]

            if won + unmarked == 3:
                if won == 2:
                    ans = ans +300*sval+10000*(sval-1000000)
                if won == 1:
                    ans = ans + 30*sval
                if won == 0:
                    ans = ans + 5*sval

        for j in range(3):
            won = 0
            unmarked = 0
            sval = 0
            for i in range(3):
                if board.small_boards_status[k][i][j] == flag:
                    won = won + 1
                if board.small_boards_status[k][i][j] == '-':
                    unmarked = unmarked + 1
                sval = sval + self.SmallValue[k][i][j]

            if won + unmarked == 3:
                if won == 2:
                    ans = ans +300*sval+10000*(sval-1000000)
                if won == 1 :
                    ans = ans + 30*sval
                if won == 0 :
                    ans = ans + 5*sval

        won = 0
        unmarked = 0
        sval = 0
        for i in range(3):
            if board.small_boards_status[k][i][i] == flag:
                won = won + 1
            if board.small_boards_status[k][i][i] == '-':
                unmarked = unmarked + 1
        
        if won + unmarked == 3:
            if won == 2:
                ans = ans+2*(300*sval+10000*(sval-1000000))
            if won == 1 :
                ans = ans + 2*(30*sval)
            if won == 0 :
                ans = ans + 10*sval

        won = 0
        unmarked = 0
        sval = 0
        for i in range(3):
            if board.small_boards_status[k][i][2-i] == flag:
                won = won + 1
            if board.small_boards_status[k][i][2-i] == '-':
                unmarked = unmarked + 1
        
        if won + unmarked == 3:
            if won == 2:
                ans = ans + 2*(300*sval+10000*(sval-1000000))
            if won == 1 :
                ans = ans + 2*(30*sval)
            if won == 0 :
                ans = ans + 5*sval*2
        self.BoardHeuristics[(self.BoardHash[k],flag)] = ans
        return ans

    def heuristic(self,board,flag):
        self.compute_block(board,flag)
        b0 = 1
        b1 = 1
        # for i in range(3):
        #     for j in range(3):
        #         if board.big_boards_status[0][i][j] == flag:
        #             b0 = b0 + 1
        #         if board.big_boards_status[0][i][j] == self.opponent(flag):
        #             b0 = b0 - 1
        #         if board.big_boards_status[1][i][j] == flag:
        #             b1 = b1 + 1
        #         if board.big_boards_status[1][i][j] == self.opponent(flag):
        #             b1 = b1 -1
        # if flag == self.Me:
        #     b0 = 3
        #     b1 = 1
        # else :
        #     b0 = 1
        #     b1 = 3
        return b0*max(self.val_big(board,0,flag),self.val_big(board,1,flag))+b1*min(self.val_big(board,0,flag),self.val_big(board,1,flag))

    # def cmpr(x,y):
    #     p = board.update(self.oldm,x,self.curr)
    #     self.addmove(x,self.curr)
    #     z = self.heuristic(board,self.Me)-self.heuristic(board,self.opponent(self.Me))
    #     self.addmove(x,self.curr)
    #     board.big_boards_status[x[0]][x[1]][x[2]] = '-'
    #     board.small_boards_status[x[0]][x[1]/3][x[2]/3] = '-'
    #     p = board.update(self.oldm,y,self.curr)
    #     self.addmove(y,self.curr)
    #     w = self.heuristic(board,self.Me)-self.heuristic(board,self.opponent(self.Me))
    #     self.addmove(y,self.curr)
    #     board.big_boards_status[y[0]][y[1]][y[2]] = '-'
    #     board.small_boards_status[y[0]][y[1]/3][y[2]/3] = '-'
    #     if self.curr == self.Me:

    def minimax(self,board,old_move,flag,alpha,beta,depth,MaxDepth,bonusMove):
        Goal = board.find_terminal_state()
        if Goal[1] == 'WON':
            if Goal[0] == self.Me:
                return self.INF,"placeholder"
            else :
                return -self.INF,"placeholder"
        
        if Goal[1] == 'DRAW':
            # return random.randrange(-self.INF,self.INF),"placeholder"
            return self.CalScoreifDraw(board),"placeholder"

        if depth == MaxDepth or self.tle<=time.time():
            # return random.randrange(-self.INF,self.INF),"placeholder"
            x=1
            y=1
            # if old_move[0] == 0 and old_move[1]/3 == 0 and old_move[2]/3 == 0:
                # print(self.heuristic(board,self.Me),old_move)
            return (x*self.heuristic(board,self.Me)-y*self.heuristic(board,self.opponent(self.Me))),"placeholder"

        valid_cells = board.find_valid_move_cells(old_move)
        self.oldm = old_move
        self.curr = flag
        # sorted(valid_cells,cmp=self.cmpr)
        My = (flag == self.Me)
        if My:
            maxVal = -self.INF
            maxInd = 0
            for i in range(len(valid_cells)):
                if self.tle <= time.time():
                    break
                move = valid_cells[i]
                swin = board.update(old_move,move,flag)
                self.addmove(move,flag)
                if swin[1] == True and bonusMove == 0:
                    val = self.minimax(board,move,flag,alpha,beta,depth+1,MaxDepth,1)[0]
                    if val > maxVal:
                        maxVal = val
                        maxInd = i
                    if maxVal > alpha:
                        alpha = maxVal
                else:
                    val = self.minimax(board,move,self.opponent(flag),alpha,beta,depth+1,MaxDepth,0)[0]
                    # if move[0] == 0 and move[1]/3 == 0 and move[2]/3 == 0:
                        # print(val,move)
                    if val > maxVal:
                        maxVal = val
                        maxInd = i
                    if maxVal > alpha:
                        alpha = maxVal
                
                board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                board.small_boards_status[move[0]][move[1]/3][move[2]/3] = '-'
                self.addmove(move,flag)
                if alpha >= beta:
                    break

                
            return maxVal,valid_cells[maxInd]

        else:
            minVal = self.INF
            minInd = 0
            for i in range(len(valid_cells)):
                if self.tle <= time.time():
                    break
                move = valid_cells[i]
                swin = board.update(old_move,move,flag)
                self.addmove(move,flag)
                if swin[1] == True and bonusMove == 0:
                    val = self.minimax(board,move,flag,alpha,beta,depth+1,MaxDepth,1)[0]
                    if val < minVal:
                        minVal = val
                        minInd = i
                    if minVal < beta:
                        beta = minVal
                else:
                    val = self.minimax(board,move,self.opponent(flag),alpha,beta,depth+1,MaxDepth,0)[0]
                    if val < minVal:
                        minVal = val
                        minInd = i
                    if minVal < beta:
                        beta = minVal
                
                board.big_boards_status[move[0]][move[1]][move[2]] = '-'
                board.small_boards_status[move[0]][move[1]/3][move[2]/3] = '-'
                self.addmove(move,flag)
                if alpha >= beta:
                    break
        
            return minVal,valid_cells[minInd]



    def move(self,board,old_move,flag):
        # print(flag)
        self.available_moves = board.find_valid_move_cells(old_move)
        self.Me = flag
        self.tle = time.time()+23
        MaxDepth = 2
        mval = -self.INF
        bestMove = self.available_moves[0]
        if old_move[0] != -1:
            if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.opponent(flag):
                self.addmove(old_move,self.opponent(flag))
        self.BoardHashcopy = deepcopy(self.BoardHash)
        self.BlockHashcopy = deepcopy(self.BlockHash)
        while True:
            move = self.minimax(board,old_move,flag,-self.INF,self.INF,0,MaxDepth,0)
            # if self.tle <= time.time():
                # break
            if move[0] > mval:
                mval = move[0]
                bestMove = move[1]
            if self.tle <= time.time():
                break
            MaxDepth += 1
        # print(MaxDepth)
        self.BoardHash = deepcopy(self.BoardHashcopy)
        self.BlockHash = deepcopy(self.BlockHashcopy)
        self.addmove(bestMove,flag)
        return bestMove


# Bot = Bot()
# mat = [ ['x','0','0'] , ['-','-','-'] , ['-','-','-'] ]
# print(Bot.value(mat,'0')-Bot.value(mat,'x'))
# mat = [ ['x','0','-'] , ['-','0','-'] , ['-','-',''] ]
# print(Bot.value(mat,'0')-Bot.value(mat,'x'))
