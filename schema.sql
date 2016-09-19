create table `acmers` (
    `id` text primary key not null,
    `name` text,
    `email` text,
    `solved` int,
    `submissions` int,
    `solved_problem_list` text,
    `last_submit_time` text,
    `update_time` real,
    `last_week_solved` int,
    `status` int
);
