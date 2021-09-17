def sudoku_as_covermatrix(sudoku):
    
    """
    Input:
        sudoku
        
    Output:
        a cover matrix that is equivalent to the sudoku
    """
    
    covermatrix = cover_matrix()
    
    #convert input sudoku into cover-matrix
    for row in range(9):
        for col in range(9):
            n = sudoku[row][col]
            if n != 0:
                for num in range(9):
                    if num+1 != n:
                        covermatrix[row*9*9+col*9+num] = 0
                        
    return covermatrix
    
    
def cover_matrix():
    #build an empty cover matrix (4 constraints against 9*9*9 different possibilites) Index is: row, col, n. i.e. 
    cover_matrix = np.zeros((9*9*9,9*9*4))

    head = -1

    #create the cell constraints
    for row in range(9):
        for col in range(9):
            head+=1
            for n in range(9):
                cover_matrix[row*9*9+col*9+n][head] = 1

    #create the row constraints
    for row in range(9):
        for n in range(9):
            head+=1
            for col in range(9):
                cover_matrix[row*9*9+col*9+n][head] = 1

    #create the column constraints
    for col in range(9):
        for n in range(9):
            head+=1
            for row in range(9):
                cover_matrix[row*9*9+col*9+n][head] = 1

    #create the box constraints
    for row in range(3):
        for col in range(3):
            for n in range(9):
                head+=1
                for rowdelta in range(3):
                    for coldelta in range(3):
                        index = (((row*3)+rowdelta)*9*9) + (((col*3)+coldelta)*9) + n
                        #print(f"Head is: {head}, Index is: {index}")
                        cover_matrix[index][head] = 1
    
    return cover_matrix

class DLX_Node():
    
    """
    A class to represent a dancing link node. Each instance has a correspinding top, bottom, left and right node as
    well as a corresponding column.
    
    It has the functions remove_left_right and remove_top_bottom to cover the node and the function insert_left_right
    and insert_top_bottom to uncover the node
    """
    
    def __init__(self, column = None):
        self.left = self
        self.right = self
        self.top = self
        self.bottom = self
        self.column = column

    def link_down(self, DLX_Node):
        DLX_Node.bottom = self.bottom
        DLX_Node.bottom.top = DLX_Node
        DLX_Node.top = self
        self.bottom = DLX_Node
        return DLX_Node
    
    def link_right(self, DLX_Node):
        DLX_Node.right = self.right
        DLX_Node.right.left = DLX_Node
        DLX_Node.left = self
        self.right = DLX_Node
        return DLX_Node
    
    def remove_left_right(self):
        self.left.right = self.right
        self.right.left = self.left
        
    def insert_left_right(self):
        self.left.right = self
        self.right.left = self
        
    def remove_top_bottom(self):
        self.top.bottom = self.bottom
        self.bottom.top = self.top
        
    def insert_top_bottom(self):
        self.top.bottom = self
        self.bottom.top = self

class Column_Node(DLX_Node):
    
    """
    A class that extends the dlx node class. It is the column node in the dancing links matrix and has a 
    corresponding name and size
    
    It also has functions cover and uncover which cover and uncover all rows that satisfy the column node.
    """
    
    def __init__(self, n):
        super().__init__()
        self.name = n
        self.column = self
        self.size = 0
    
    def cover(self):
        self.remove_left_right()
        i = self.bottom
        while i != self:
            j = i.right
            while j != i:
                j.remove_top_bottom()
                j.column.size -= 1
                j = j.right
            i = i.bottom
        
    def uncover(self):
        i = self.top
        while i != self:
            j = i.left
            while j != i:
                j.column.size += 1
                j.insert_top_bottom()
                j = j.left
            i = i.top
        self.insert_left_right()
        
class DLX():
    
    """
    A class to contain all the code for solving a cover matrix.
    - create_DLX_board(covermatrix) creates a dancing link matrix from an input cover matrix
    - algorithm_x() solves the sudoku by selecting a col, covering it and then trialing each row that is in that 
        col and then calling itself until it reaches a solution. If it can't continue it backtracks and trials 
        the next row in the chosen column
    - select_col_node() returns a column node with the smallest size
    - parse_board(answer) parses the answer into a filled in sudoku
    """
    
    def __init__(self, covermatrix):
        self.head = self.create_DLX_board(covermatrix)
        self.answer = []
        self.result = []
        
    def create_DLX_board(self, covermatrix):
        no_of_columns = len(covermatrix[0])
        head_node = Column_Node("header")
        column_nodes = []
        
        for i in range(no_of_columns):
            n = Column_Node(f"{i}")
            column_nodes.append(n)
            head_node = head_node.link_right(n)
            
        head_node = head_node.right.column
        
        for row in covermatrix:
            prev = None
            for j in range(no_of_columns):
                if row[j] == 1:
                    col = column_nodes[j]
                    node = DLX_Node(column = col)
                    if prev == None:
                        prev = node
                    col.top.link_down(node)
                    prev = prev.link_right(node)
                    col.size += 1
        head_node.size = no_of_columns
        
        return head_node
    
    def algorithm_x(self, k):
        if self.head.right == self.head:
            result = self.parse_board(self.answer)
            return result
        else:
            col = self.select_col_node()
            col.cover()
            i = col.bottom
            while i != col:
                self.answer.append(i)
                j = i.right
                while j != i:
                    j.column.cover()
                    j = j.right
                result = self.algorithm_x(k+1)
                if hasattr(result, 'shape'):
                    return result
                i = self.answer.pop()
                col = i.column
                j = i.left
                while j != i:
                    j.column.uncover()
                    j = j.left  
                i = i.bottom
            col.uncover()
    
    def select_col_node(self):
        col = self.head.right
        minimum = col.size
        min_col = col
        while col != self.head:
            if col.size < minimum:
                minimum = col.size
                min_col = col
            col = col.right
        return min_col
            
    def parse_board(self, answer):
        result = np.zeros((9,9))
        for node in answer:
            rcnode = node
            minimum = int(rcnode.column.name)
            tmp = node.right
            count = 1
            while tmp != node:
                val = int(tmp.column.name)
                if val < minimum:
                    minimum = val
                    rcnode = tmp
                tmp = tmp.right
                    
            ans1 = int(rcnode.column.name)
            ans2 = int(rcnode.right.column.name)
            row = ans1 // 9
            col = ans1 % 9
            num = ans2%9 + 1
            result[row][col] = num
        return result
    
def depth_first_solver(sudoku):    
    """
    Solves a Sudoku puzzle and returns its unique solution.

    Input
        sudoku : 9x9 numpy array
            Empty cells are designated by 0.

    Output
        9x9 numpy array of integers
            It contains the solution, if there is one. If there is no solution, all array entries should be -1.
    """
    #check that the current sudoku is allowable
    for y in range(9):
        for x in range(9):
            if sudoku[y][x] != 0:
                n = sudoku[y][x]
                sudoku[y][x] = 0
                if allowable_move(y, x, n, sudoku):
                    sudoku[y][x] = n
                    continue
                else:
                    return np.full((9,9), -1)
    
    #if allowable find the correct solution
    solution = depth_first(sudoku)
    
    if 0 not in solution:
        return solution
    return np.full((9,9), -1)

def depth_first(sudoku):
    for y in range(9):
        for x in range(9):
            if sudoku[y][x] == 0:
                for n in range(1,10):
                    if allowable_move(y, x, n, sudoku):
                        sudoku[y][x] = n
                        sudoku = depth_first(sudoku)
                        if 0 not in sudoku:
                            return sudoku
                        #backtracks+=1
                        sudoku[y][x] = 0
                return sudoku
    return sudoku                     

def allowable_move(y, x, n, sudoku):
    """
    Checks if n, placed at location y, x on sudoku is an allowable move by checking the x-axis, the y-axis, 
        and the 3 by 3 box that it is in.
    
    """
    for i in range(9):
        if sudoku[y][i] == n:
            return False
        elif sudoku[i][x] == n:
            return False
    xbox = (x//3) * 3
    ybox = (y//3) * 3
    for i in range(3):
        for j in range(3):
            if sudoku[ybox+i][xbox+j] == n:
                return False
    return True 

def sudoku_solver(sudoku):
    """
    If the sudoku has 20 or less empty cells then the function calls
    """
    if np.count_nonzero(sudoku==0) <= 20:
        answer = depth_first_solver(sudoku)
        return answer
    x = DLX(sudoku_as_covermatrix(sudoku))
    answer = x.algorithm_x(0)
    if hasattr(answer, 'shape'):
        if 0 in answer:
            return np.full((9,9), -1)
        return answer
    else:
        return np.full((9,9), -1)