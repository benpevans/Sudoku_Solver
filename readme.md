# AI Sudoku Solver

The presented solution utilises two different algorithms, depending upon the sudokus complexity, to automatically solve any sudoku that it is given. The first is a simple backtracking, depth-first search algorithm. The second models the sudoku as an exact cover problem and utilises Donald Knuths Dancing Links algorithm.

#### Depth-First Search

The initial, depth-first search solution first checks the input sudoku is a valid configuration by looping through all the entries in the sudoku. If an entry is non-zero it sets that entry, n to zero and calls `allowable_move(y, x, n, sudoku)` with the sudoku and n as input as well as its x and y locations. `allowable_move(y, x, n, sudoku)` checks that none of the entries in the x and y directions and box location are equal to n. If `allowable_move(y, x, n, sudoku)` returns `True`, then the sudoku is reset back to have value n at location x, y. If any of the locations return `False` then the solver breaks and returns a 9x9 numpy array of -1. If all locations return `True` then `depth_first_solver(sudoku)` calls `depth_first(sudoku)`, the actual solving algorithm.

`depth_first(sudoku)` is a depth-first search algorithm as it exhaustively explores each branch it finds in its search. To do this, it loops through the entries in the sudoku until it finds a location equal to 0. The solver tries to fill the location by working through the numbers 1 to 9 and checking if it is valid by calling `allowable_move(y, x, n, sudoku)`. If it is valid, the solver sets that location to n and recursively calls itself again and attempts to fill the next non-zero location. If the solver cannot find a valid move in the next location, it will backtrack and try the next valid move in the previous step. At the point where the function stops, it will return the sudoku in its current state to the function `depth_first_solver(sudoku)` which then returns the corresponding output of 9x9 array of -1's if there is no solution or a solved sudoku if there is one.

During testing, the alogrithm proved extremely quick at solving all puzzles up to the hard difficulty. This is because for the simpler sudokus, the possible search space is much smaller as there are fewer empty entrys in the sudoku. As the number of empty entrys becomes larger, the search space becomes exponentially bigger. Figure 1 shows the number of zeros and corresponding mean time to complete in seconds.

![img](Mean_No_of_zeros.png)
*Figure 1: The average number of empty entries for each sudoku difficulty and its corresponding performance of `depth_first_solver(sudoku)` in seconds*

To further improve the algorithm, the entries could be selected smartly however, adding more heuristics could have the effect of slowing down the process time for the very easy to medium difficulty sudokus. Because of this, a completely different algorithm could be chosen for sudokus which have more than 20 empty entries. One such algorithm that is able to quickly deal with more complex sudokus was found to be Donald Knuth's dancing links.

#### Dancing Links
Dancing Links, popularised by Donald Knuth, is an alogrithm which can greatly improve the speed of depth-first search problems. To implement it, the sudoku first needs to be represented as an exact cover problem. 
##### Exact cover matrix
An exact cover problem is where, given a set of choices and a set of constraints, is there a solution such that a selection of choices fills each constraint once. In the context of sudoku, there are 4 constraints, namely:
1. Each cell must be filled once (81 cells so 81 constraints)
2. Each row must have the values 1 to 9 occur only once (9 values x 9 rows = 81 constraints)
3. Each column must have the values 1 to 9 occur only once (9 values x 9 columns = 81 constraints)
4. Each sub-square must have values 1 to 9 occur only once (9 values x 9 sub-squares = 81 constraints)  

This gives a total of 4 x 81 constraints = 324 constraints/columns. There are 81 cells and each cell can have a value 1 to 9 so there are 9 x 81 possible choices = 729 choices/rows. This can be represented as a numpy matrix of 1s and 0s with a 1 representing where a constraint has been satisfied. All the columns must have only one 1 in them, when a choice is made/row is selected then we cover all the other rows that also have a 1 in that column

To represent an input sudoku as a cover matrix there are two functions. `sudoku_as_covermatrix(sudoku)` and `cover_matrix()`. `sudoku_as_covermatrix(sudoku)` takes an input sudoku and returns a cover matrix that represents that sudoku. It first calls `cover_matrix()` to build a cover matrix that contains all possible inputs. `cover_matrix()` first creates an 2D numpy array of 0s with shape 729 x 324. The array is then filled with 1s where a choice corresponds to a constraint, i.e. for a choice of row 1, col 1, \#1 (the first row in the numpy array), there would be 4 1s.
- 1 in col 0 to represent the first cell being filled, 
- 1 in col 81 to represent the first row having a value of 1
- 1 in col 162 to represent the first col having a value of 1 (162 - 81 = 81)
- 1 in col 243 to represet the first box having a value of 1  

And so forth until the whole matrix is filled. This array is then returned to the function `sudoku_as_covermatrix(sudoku)` which then covers the matrix rows where the input sudoku already satifies the constraint

#### Dancing Links
Now the sudoku is represented as a cover matrix, it is possible to solve it using the Dancing Links algorithm. Figure 2 shows how this concept works, each 1 in our cover matrix is represented by a node of a doubly linked list. This has the benefit of removing the need to search through the matrix to find 1s and also allows for better implementation of removing and replacing nodes as the algorithm conducts its search.
![img](Dancing_Links.png)
*Figure 2: Dancing links matrix, source:  https://www.geeksforgeeks.org/exact-cover-problem-algorithm-x-set-2-implementation-dlx/*

To represent a node in the dancing links matrix there is the class `DLX_Node()`. Each instance has an associated left, right, top and bottom node as well as an associated column node. To represent the column nodes as seen in figure 2, there is a column node class `Column_Node(DLX_Node)` which extends `DLX_Node()` but also has an associated name and size. 

- The dlx node class has the functions `link_down(DLX_Node)` and `link_right(DLX_Node)` which link two DLX nodes together. 
- The dlx node class also has the function `remove_left_right()` to remove the node from the matrix. If we want to delete node x then we set `x.left.right = x.right` and `x.right.left = x.left`. The same is analogous to `remove_top_bottom()`. 
- If we want to uncover node x then there is the function `insert_left_right()` which sets `x.left.right = x` and `x.right.left = x`. The same is analogous to the function `insert_top_bottom()`. 
- The column node class has the functions `cover()` and `uncover()`. If a constraint has been satisified and therefore we want to cover column n then `cover()` works by covering all the nodes that correspond to column n as well as the nodes that correspond to each row that is in n. This is done by utilising the DLX node functions `remove_top_bottom()` and `remove_left_right()`. The same is conversely true for `uncover()`.  

The class `DLX()` takes in an input cover matrix and represents it as a dancing links matrix using the `create_DLX_board(covermatrix)` function. It loops through the cover matrix and creates a DLX node if it finds a 1 and links that node to its corresponding top, bottom, left, and right nodes.

After creating the board, we can call the function `algorithm_x()` to solve the sudoku. It is a recursive, backtracking, depth-first search algorithm similar to the original solution. If the size of the dancing links matrix is 1 then it is solved (all constraints have been satisfied and covered), else it will recursively call itself. `algorithm_x()` selects a column node by calling the function `select_col_node()` which returns the column node with the smallest size. This is an optimisation heuristic to allow the dancing links algorithm to perform faster. `algorithm_x()` covers the column that is returned and appends the first col.bottom node to the answer. It then covers all the columns that correspond to the nodes in the row of col.bottom. The function then recursively calls itself until it has reached a solution. If the algorithm finds there is not a possible solution then it backtracks and trials col.bottom.bottom. This pattern continues until it finds itself back at the original column node. If this happens then there is no solution.

Finally the function `parse_board()` takes the output of `algorithm_x()` and returns tbe solution as a 9x9 sudoku array.

The performance of the dancing links algorithm greatly improves upon the initial solving algorithm. It has a mean solve time of 0.01 seconds and shows negligble variation in time to complete between the very easy to hard difficulties. This gives it a total solve time of 5.97 seconds for all 60 sudokus.

#### Combining algorithms

As figure 1 shows, the original algorithm remains faster for the very easy to medium difficulty sudokus. Therefore the final solution uses a combination of both algorithms. If the input sudoku has less than 20 empty cells, then it runs the original `depth_first_solver(sudoku)`. If it has more then it runs the dancing links algorithm. By combining both algorithms, the total time for solving all 60 sudokus is now 1.55 seconds.

An improvement would be to more accurately chose which of the two algorithms is better as a function of the number of empty cells rather than arbitrarily set it to when there is more than 20 empty cells. However to do this, a greater data set of example sudokus is needed with more variation between medium and hard sudokus.

#### References
- Knuth D. (2000) 'Dancing Links' \[online\]. Millenial Perspectives in Computer Science. pgs 187--214. Available from: https://arxiv.org/pdf/cs/0011047.pdf
- GeeksforGeeks. (2017). Exact Cover Problem and Algorithm X | Set 2 (Implementation with DLX). [online] Available at: https://www.geeksforgeeks.org/exact-cover-problem-algorithm-x-set-2-implementation-dlx/ [Accessed 15 Mar. 2021].
- Saurel, S. (2019). Building A Sudoku Solver In Java With Dancing Links. [online] Medium. Available at: https://medium.com/javarevisited/building-a-sudoku-solver-in-java-with-dancing-links-180274b0b6c1.
