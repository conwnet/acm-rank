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
    `update_time` text,
    `status` int
);

insert into `acmers` (`id`, `name`, `status`) values ('0', 'b707a6620ecf72d4608e789ca1ec29030236ba75371d4d81738f98f2fcbc1277', 0);
