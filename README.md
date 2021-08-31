# Maze-Creator
This Python script generates Maze puzzles with given sizes

1) Program starts with a maze grid filled by only the walls. 
2) Then from the starting position (which is top left) a "rolling stone" starts to roll from that starting position.
3) In each step in it's roll movement, it moves 2 unit ahead. 
4) When it reaches a position where there is more than one valid directions it can roll to, it saves this position to a dictionary and selects one direction randomly.
5) If it reaches a position where there is no valid direction it can roll to except the opposite of it's current direction, it starts rolling backwards.
6) When it starts rolling backwards, it goes to the last (or first depending on difficulty of the puzzle) it returns to the position where there was more than one valid directions.
7) And keeps going where there is no more saved direction in the dictionary(4th)
8) While rolling it keeps tracking valid ending positions and the distance from starting position to the ending position.
9) When there is no more saved direction in the dictionary(4th) it takes the furthest valid ending position and marks this position as ending position
10) If there is no valid ending points (such a chance you got) it makes the whole process again.

author: Kerem Kırıcı
mail: kerem.kirici36@gmail.com
