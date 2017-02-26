Python and MySQL-based Priority Management application.

A simple desktop GUI to manage and view current, archived, and completed priorities housed within a database. Tasks are assigned a weight and ranked per the aggregate of relative importance, urgency, and difficulty. Weight calculation is based on the WSPT scheduling algorithm (Weighted Shortest Processing Time, referenced below) – adjusting additionally for a priority's due-date, when provided.

Setup requires a database connection, with configuration specified in "/application/PriorityManager.conf".

> [Weighted Shortest Processing Time] is a pretty good candidate for best general-purpose scheduling strategy in the face of uncertainty. It offers a simple prescription for time management: each time a new piece of work comes in, divide its importance by the amount of time it will take to complete. If that figure is higher than for the task you’re currently doing, switch to the new one; otherwise stick with the current task. This algorithm is the closest thing that scheduling theory has to a skeleton key or Swiss Army knife, the optimal strategy not just for one flavor of problem but for many. Under certain assumptions it minimizes not just the sum of weighted completion times, as we might expect, but also the sum of the weights of the late jobs and the sum of the weighted lateness of those jobs.
> 
> – _[Algorithms to Live By: The Computer Science of Human Decisions][1]_ by Brian Christian, Tom Griffiths

[1]: http://a.co/32KO6lW
