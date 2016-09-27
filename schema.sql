create table `acmers` (
    `id` text primary key not null,
    `name` text,
    `email` text,
    `submissions` int,
    `solved` int,
    `solved_problem_list` text,
    `last_submit_time` text,
    `previous_solved` text,
    `previous_solved_problem_list` text,
    `update_time` real,
    `status` int
);
