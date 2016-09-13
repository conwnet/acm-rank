create table `acmers` (
    `id` text primary key not null,
    `name` text not null,
    `email` text not null,
    `solved` int not null,
    `submissions` int not null,
    `solved_problem_list` text not null,
    `last_submit_time` real not null,
    `update_time` real not null,
    `last_week_solved` int not null,
    `status` int not null
);
