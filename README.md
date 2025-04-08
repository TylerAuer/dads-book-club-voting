# Dad's Book Club Selection Algorithm

This is a script I wrote for helping my book club select books to read. We rank a set of books in
order of preference, and this program decides which book(s) we'll read.

It's a custom algorithm because I wanted to allow for possibility of selecting multiple books. The algorithm has three assumptions:

- Each person is always assigned to read the highest rank book in the chosen set of books -- people want to read the book they ranked highest
- We only consider combinations of books where the above is true and where each book has a minimum number of people assigned to it -- you need some minimum number of people to discuss a book
- Each person will only read one book -- we don't want to assign people to read multiple books (although it won't really mess things up if they do)

We consider each person's "score" to be the rank of the book they are assigned to read -- lower is better.

Given the above, we consider every combination of books from 1 to n, where n is the number of books. For example, given books A, B, and C, we consider the following cominations:

- A
- B
- C
- A, B
- A, C
- B, C
- A, B, C

For each combination, we assign each person to the book they rank most highly. If after that each book has enough people, we calculate the [root mean square](https://en.wikipedia.org/wiki/Root_mean_square) of each person's score after assigning. The combination with lowest root mean square (and enough people in each group) is the winner.

## Why root mean square?

The root mean square has a greater penalty for people getting stuck with books they prefer less.
