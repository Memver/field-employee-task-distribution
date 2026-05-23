INSERT INTO public.role
(
	id, name
)
	VALUES 
	(1, 'ADMIN'),
	(2, 'EMPLOYEE_MANAGER'),
	(3, 'FIELD_EMPLOYEE'),
	(4, 'AGENT_POINT_MANAGER');

INSERT INTO public.grade
(
	id, name, level
)
	VALUES 
	(1, 'JUNIOR', 10),
	(2, 'MIDDLE', 60),
	(3, 'SENIOR', 110);

INSERT INTO public.location
(
	id, address, lat, lon
)
	VALUES 
	(1, 'Россия, Краснодар, Красная, 139', 45.0449862, 38.9765876),
    (2, 'Россия, Краснодар, В.Н. Мачуги, 41', 45.0128578, 39.0717488),
    (3, 'Россия, Краснодар, Красных Партизан, 321', 45.0514211, 38.9564249),
	(4, 'Россия, Краснодар, тер. Пашковский жилой массив, Крылатая, 2', 45.0113787, 39.122462),
	(5, 'Россия, Краснодар, Восточно-Кругликовская, 64/2', 45.06876395, 39.02560522382217),
	(6, 'Россия, Краснодар, ст-ца. Елизаветинская, Широкая, 260', 45.049406250000004, 38.803343999999996),
	(7, 'Россия, Краснодар, Уральская, 79/1', 45.0344911, 39.052518),
	(8, 'Россия, Краснодар, им. Селезнева, 197/5', 45.0165901, 39.0541191),
	(9, 'Россия, Краснодар, Красная, 149', 45.048263250000005, 38.97818755881007),
	(10, 'Россия, Краснодар, им. Володи Головатого, 313', 45.0392504, 38.9744738),
	(11, 'Россия, Краснодар, Красноармейская, 126', 45.0540287, 38.78333182918455),
	(12, 'Россия, Краснодар, Ленина, 37', 45.02088465, 39.08052255),
	(13, 'Россия, Краснодар, Красных Партизан, 439', 45.0514211, 38.9564249),
	(14, 'Россия, Краснодар, Таманская, 153', 45.023305050000005, 39.01281960716355),
	(15, 'Россия, Краснодар, Дзержинского, 165', 45.0902859, 38.97646804701084),
	(16, 'Россия, Краснодар, Тургенева, 174', 45.0697697, 38.970178925216445),
	(17, 'Россия, Краснодар, Ставропольская, 140', 45.01989315, 39.003858446928824),
	(18, 'Россия, Краснодар, Уральская, 162', 45.0385151, 39.09396181038221),
	(19, 'Россия, Краснодар, Атарбекова, 24', 45.0591141, 38.9492965),
	(20, 'Россия, Краснодар, Героя Аверкиева, 8', 45.060213399999995, 39.029274322484525),
	(21, 'Россия, Краснодар, Тургенева, 106', 45.052193349999996, 38.95986561799339),
	(22, 'Россия, Краснодар, Красная, 145', 45.046872449999995, 38.97772153508214),
	(23, 'Россия, Краснодар, Красная, 154', 45.037148, 38.975632821148466),
	(24, 'Россия, Краснодар, Красных Партизан, 117', 45.0634423, 38.9191145),
	(25, 'Россия, Краснодар, Северная, 389', 45.0375616, 38.9935016),
	(26, 'Россия, Краснодар, Уральская, 166/3', 45.0390135, 39.0955714),
	(27, 'Россия, Краснодар, Северная, 524', 45.0360279, 39.001249327204974),
	(28, 'Россия, Краснодар, Коммунаров, 258', 45.0436991, 38.9814975),
	(29, 'Россия, Краснодар, Дзержинского, 101', 45.069402350000004, 38.972340575108305),
	(30, 'Россия, Краснодар, Северная, 326', 45.0406511, 38.970659),
	(31, 'Россия, Краснодар, Красная, 176', 45.04589, 38.981377),
	(32, 'Россия, Краснодар, Дзержинского, 102', 45.1037667, 38.9840094);

INSERT INTO public.priority
(
	id, name, level
)
	VALUES 
	(1, 'LOW', 10),
	(2, 'MIDDLE', 60),
	(3, 'HIGH', 110);

INSERT INTO public.task_status
(
	id, name
)
	VALUES 
	(1, 'ASSIGNED'),
	(2, 'COMPLETED'),
	(3, 'SKIPPED');

INSERT INTO public.user
(
	id, role_id, login, hashed_password, name, surname, middle_name, is_superuser
)
	VALUES
    (1, 3, 'deryagin', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Никита', 'Дерягин', 'Владимирович', false),
    (2, 3, 'petroshev', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Валерий', 'Петрошев', 'Павлович', false),
    (3, 3, 'evdokimov', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Давид', 'Евдокимов', 'Тихонович', false),
    (4, 3, 'andreev', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Гордий', 'Андреев', 'Данилович', false),
    (5, 3, 'ivanov', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Адам', 'Иванов', 'Федорович', false),
    (6, 3, 'bobylev', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Ипполит', 'Бобылёв', 'Альбертович', false),
    (7, 3, 'belyaeva', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Евгения', 'Беляева', 'Антоновна', false),
    (8, 3, 'nikolaev', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Азарий', 'Николаев', 'Платонович', false),
	(9, 1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Валерий', 'Евдокимов', 'Данилович', true),
	(10, 2, 'manager', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Давид', 'Лебедев', 'Платонович', false),
    (11, 4, 'ap_manager', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'Адам', 'Соколов', 'Федорович', false);

INSERT INTO public.employee
(
	id, user_id, grade_id, start_location_id
)
	VALUES
	-- Дерягин Никита Владимирович (Синьор -> grade_id = 3), Локация "Красная, 139" -> location_id = 1
    (1, 1, 3, 1),
    -- Петрошев Валерий Павлович (Мидл -> grade_id = 2), Локация "Красная, 139" -> location_id = 1
    (2, 2, 2, 1),
    -- Евдокимов Давид Тихонович (Джун -> grade_id = 1), Локация "Красная, 139" -> location_id = 1
    (3, 3, 1, 1),
    -- Андреев Гордий Данилович (Синьор -> grade_id = 3), Локация "Мачуги, 41" -> location_id = 2
    (4, 4, 3, 2),
    -- Иванов Адам Федорович (Мидл -> grade_id = 2), Локация "Мачуги, 41" -> location_id = 2
    (5, 5, 2, 2),
    -- Бобылёв Ипполит Альбертович (Джун -> grade_id = 1), Локация "Мачуги, 41" -> location_id = 2
    (6, 6, 1, 2),
    -- Беляева Евгения Антоновна (Мидл -> grade_id = 2), Локация "Красных Партизан, 321" -> location_id = 3
    (7, 7, 2, 3),
    -- Николаев Азарий Платонович (Джун -> grade_id = 1), Локация "Красных Партизан, 321" -> location_id = 3
    (8, 8, 1, 3);

INSERT INTO public.task_type
(
	id, name, execution_time, min_grade_id, priority_id
)
	VALUES 
	-- (priority HIGH, min grade SENIOR)
	(1, 'SALES_STIMULATION', 4, 3, 3),
	-- (priority MIDDLE, perform_time 2ч, min grade MIDDLE)
	(2, 'AGENT_TRAINING', 2, 2, 2),
	-- (priority LOW, perform_time 1.5ч, min grade JUNIOR)
	(3, 'CARDS_DELIVERY', 1.5, 1, 1);


INSERT INTO public.agent_point
(
    id, location_id, created_time
)
VALUES
    -- Базовая дата среза датасета: 2023-01-02 (вчера), 2022-12-01 (давно)
    (1, 4, '2022-12-01 00:00:00+00'::timestamptz),
    (2, 5, '2022-12-01 00:00:00+00'::timestamptz),
    (3, 6, '2022-12-01 00:00:00+00'::timestamptz),
    (4, 7, '2022-12-01 00:00:00+00'::timestamptz),
    (5, 8, '2022-12-01 00:00:00+00'::timestamptz),
    (7, 9, '2022-12-01 00:00:00+00'::timestamptz),
    (8, 10, '2022-12-01 00:00:00+00'::timestamptz),
    (9, 11, '2022-12-01 00:00:00+00'::timestamptz),
    (10, 12, '2022-12-01 00:00:00+00'::timestamptz),
    (11, 13, '2022-12-01 00:00:00+00'::timestamptz),
    (12, 14, '2022-12-01 00:00:00+00'::timestamptz),
    (13, 15, '2022-12-01 00:00:00+00'::timestamptz),
    (14, 16, '2023-01-02 00:00:00+00'::timestamptz),
    (15, 17, '2023-01-02 00:00:00+00'::timestamptz),
    (16, 18, '2022-12-01 00:00:00+00'::timestamptz),
    (17, 19, '2023-01-02 00:00:00+00'::timestamptz),
    (18, 20, '2022-12-01 00:00:00+00'::timestamptz),
    (19, 21, '2022-12-01 00:00:00+00'::timestamptz),
    (20, 22, '2022-12-01 00:00:00+00'::timestamptz),
    (21, 23, '2023-01-02 00:00:00+00'::timestamptz),
    (22, 24, '2023-01-02 00:00:00+00'::timestamptz),
    (23, 25, '2022-12-01 00:00:00+00'::timestamptz),
    (24, 26, '2022-12-01 00:00:00+00'::timestamptz),
    (25, 27, '2022-12-01 00:00:00+00'::timestamptz),
    (26, 28, '2022-12-01 00:00:00+00'::timestamptz),
    (27, 29, '2022-12-01 00:00:00+00'::timestamptz),
    (28, 30, '2022-12-01 00:00:00+00'::timestamptz),
    (29, 31, '2022-12-01 00:00:00+00'::timestamptz),
    (31, 32, '2022-12-01 00:00:00+00'::timestamptz);

INSERT INTO public.agent_point_manager
(
    agent_point_id, user_id
)
VALUES
    (1, 11);

INSERT INTO public.agent_point_event
(
    agent_point_id, event_time, event_type, metric_name, metric_value_bool
)
SELECT
    id,
    event_time::timestamptz,
    'cards_delivery_status_changed',
    'is_cards_delivered',
    is_cards_delivered
FROM (
    VALUES
        (1, '2023-01-01 00:00:00+00'::timestamptz, true),
        (2, '2023-01-01 00:00:00+00'::timestamptz, true),
        (3, '2023-01-01 00:00:00+00'::timestamptz, true),
        (4, '2023-01-01 00:00:00+00'::timestamptz, false),
        (5, '2023-01-01 00:00:00+00'::timestamptz, true),
        (7, '2023-01-01 00:00:00+00'::timestamptz, true),
        (8, '2023-01-01 00:00:00+00'::timestamptz, true),
        (9, '2023-01-01 00:00:00+00'::timestamptz, true),
        (10, '2023-01-01 00:00:00+00'::timestamptz, false),
        (11, '2023-01-01 00:00:00+00'::timestamptz, true),
        (12, '2023-01-01 00:00:00+00'::timestamptz, true),
        (13, '2023-01-01 00:00:00+00'::timestamptz, true),
        (14, '2023-01-01 00:00:00+00'::timestamptz, false),
        (15, '2023-01-01 00:00:00+00'::timestamptz, false),
        (16, '2023-01-01 00:00:00+00'::timestamptz, true),
        (17, '2023-01-01 00:00:00+00'::timestamptz, false),
        (18, '2023-01-01 00:00:00+00'::timestamptz, true),
        (19, '2023-01-01 00:00:00+00'::timestamptz, true),
        (20, '2023-01-01 00:00:00+00'::timestamptz, true),
        (21, '2023-01-01 00:00:00+00'::timestamptz, false),
        (22, '2023-01-01 00:00:00+00'::timestamptz, false),
        (23, '2023-01-01 00:00:00+00'::timestamptz, true),
        (24, '2023-01-01 00:00:00+00'::timestamptz, true),
        (25, '2023-01-01 00:00:00+00'::timestamptz, true),
        (26, '2023-01-01 00:00:00+00'::timestamptz, true),
        (27, '2023-01-01 00:00:00+00'::timestamptz, true),
        (28, '2023-01-01 00:00:00+00'::timestamptz, true),
        (29, '2023-01-01 00:00:00+00'::timestamptz, true),
        (31, '2023-01-01 00:00:00+00'::timestamptz, false)
) AS seed(id, event_time, is_cards_delivered);

INSERT INTO public.agent_point_event
(
    agent_point_id, event_time, event_type, metric_name, metric_value_num
)
SELECT
    id,
    event_time::timestamptz,
    'approved_applications_changed',
    'approved_applications',
    approved_applications
FROM (
    VALUES
        (1, '2023-01-01 00:00:00+00'::timestamptz, 19),
        (2, '2023-01-01 00:00:00+00'::timestamptz, 19),
        (3, '2023-01-01 00:00:00+00'::timestamptz, 29),
        (4, '2023-01-01 00:00:00+00'::timestamptz, 5),
        (5, '2023-01-01 00:00:00+00'::timestamptz, 14),
        (7, '2023-01-01 00:00:00+00'::timestamptz, 10),
        (8, '2023-01-01 00:00:00+00'::timestamptz, 65),
        (9, '2023-01-01 00:00:00+00'::timestamptz, 38),
        (10, '2023-01-01 00:00:00+00'::timestamptz, 14),
        (11, '2023-01-01 00:00:00+00'::timestamptz, 84),
        (12, '2023-01-01 00:00:00+00'::timestamptz, 15),
        (13, '2023-01-01 00:00:00+00'::timestamptz, 19),
        (14, '2023-01-01 00:00:00+00'::timestamptz, 0),
        (15, '2023-01-01 00:00:00+00'::timestamptz, 0),
        (16, '2023-01-01 00:00:00+00'::timestamptz, 21),
        (17, '2023-01-01 00:00:00+00'::timestamptz, 6),
        (18, '2023-01-01 00:00:00+00'::timestamptz, 18),
        (19, '2023-01-01 00:00:00+00'::timestamptz, 96),
        (20, '2023-01-01 00:00:00+00'::timestamptz, 20),
        (21, '2023-01-01 00:00:00+00'::timestamptz, 0),
        (22, '2023-01-01 00:00:00+00'::timestamptz, 0),
        (23, '2023-01-01 00:00:00+00'::timestamptz, 16),
        (24, '2023-01-01 00:00:00+00'::timestamptz, 43),
        (25, '2023-01-01 00:00:00+00'::timestamptz, 13),
        (26, '2023-01-01 00:00:00+00'::timestamptz, 45),
        (27, '2023-01-01 00:00:00+00'::timestamptz, 19),
        (28, '2023-01-01 00:00:00+00'::timestamptz, 20),
        (29, '2023-01-01 00:00:00+00'::timestamptz, 82),
        (31, '2023-01-01 00:00:00+00'::timestamptz, 10)
) AS seed(id, event_time, approved_applications);

INSERT INTO public.agent_point_event
(
    agent_point_id, event_time, event_type, metric_name, metric_value_num
)
SELECT
    seed.agent_point_id,
    (
        ap.created_time
        + (
            (DATE '2023-01-02' - ap.created_time::date)
            - seed.days_after_last_card
        ) * INTERVAL '1 day'
    )::timestamptz,
    'cards_gived_changed',
    'cards_gived',
    seed.cards_gived
FROM (
    VALUES
        (1, 12, 1),
        (2, 27, 12),
        (3, 15, 15),
        (4, 0, 0),
        (5, 7, 3),
        (7, 9, 7),
        (8, 6, 12),
        (9, 0, 23),
        (10, 0, 0),
        (11, 33, 63),
        (12, 2, 1),
        (13, 0, 0),
        (14, 0, 0),
        (15, 0, 0),
        (16, 4, 5),
        (17, 0, 0),
        (18, 6, 6),
        (19, 2, 20),
        (20, 3, 4),
        (21, 0, 0),
        (22, 0, 0),
        (23, 0, 0),
        (24, 3, 29),
        (25, 3, 4),
        (26, 16, 30),
        (27, 1, 4),
        (28, 3, 9),
        (29, 76, 72),
        (31, 0, 0)
) AS seed(agent_point_id, days_after_last_card, cards_gived)
JOIN public.agent_point AS ap ON ap.id = seed.agent_point_id;

INSERT INTO public.task
(
	id, employee_id, agent_point_id, start_time, finish_time, task_type_id, task_status_id, comment
)
	VALUES 
	/*
	vehicle 0 = employee id 1
	point 0 = location id 1

	Objective: 3197397

	Route for vehicle 0:
	0 ->  9 ->  26 ->  19 ->  4 ->  16 ->  24 ->  22 ->  29 -> 0
	Distance of the route: 28039m
	Number of visits: 8

	Route for vehicle 1:
	0 ->  15 ->  31 ->  14 ->  28 ->  30 ->  27 ->  8 ->  21 -> 0
	Distance of the route: 21694m
	Number of visits: 8

	Route for vehicle 3:
	1 ->  7 ->  13 ->  6 ->  17 ->  25 ->  11 ->  3 -> 1
	Distance of the route: 30511m
	Number of visits: 7

	Route for vehicle 6:
	2 ->  12 ->  23 ->  5 ->  18 ->  20 -> 2
	Distance of the route: 29785m
	Number of visits: 5

	Route for vehicle 7:
	2 ->  10 -> 2
	Distance of the route: 30568m
	Number of visits: 1

	Maximum of the route distances: 30568m
	*/
	(1, 1, 8, '2026-03-01 08:00:00+00'::timestamptz, '2026-03-01 09:00:00+00'::timestamptz, 1, 1, ''),
	(2, 1, 25, '2026-03-01 09:00:00+00'::timestamptz, '2026-03-01 10:00:00+00'::timestamptz, 1, 1, ''),
	(3, 1, 18, '2026-03-01 10:00:00+00'::timestamptz, '2026-03-01 11:00:00+00'::timestamptz, 1, 1, ''),
	(4, 1, 2, '2026-03-01 11:00:00+00'::timestamptz, '2026-03-01 12:00:00+00'::timestamptz, 1, 1, ''),
	(5, 1, 15, '2026-03-01 12:00:00+00'::timestamptz, '2026-03-01 13:00:00+00'::timestamptz, 1, 1, ''),
	(6, 1, 23, '2026-03-01 13:00:00+00'::timestamptz, '2026-03-01 14:00:00+00'::timestamptz, 1, 1, ''),
	(7, 1, 21, '2026-03-01 14:00:00+00'::timestamptz, '2026-03-01 15:00:00+00'::timestamptz, 1, 1, ''),
	(8, 1, 28, '2026-03-01 15:00:00+00'::timestamptz, '2026-03-01 16:00:00+00'::timestamptz, 1, 1, ''),
	(9, 2, 14, '2026-03-01 08:00:00+00'::timestamptz, '2026-03-01 09:00:00+00'::timestamptz, 1, 1, ''),
	(10, 2, 31, '2026-03-01 09:00:00+00'::timestamptz, '2026-03-01 10:00:00+00'::timestamptz, 1, 1, ''),
	(11, 2, 13, '2026-03-01 10:00:00+00'::timestamptz, '2026-03-01 11:00:00+00'::timestamptz, 1, 1, ''),
	(12, 2, 27, '2026-03-01 11:00:00+00'::timestamptz, '2026-03-01 12:00:00+00'::timestamptz, 1, 1, ''),
	(13, 2, 29, '2026-03-01 12:00:00+00'::timestamptz, '2026-03-01 13:00:00+00'::timestamptz, 1, 1, ''),
	(14, 2, 26, '2026-03-01 13:00:00+00'::timestamptz, '2026-03-01 14:00:00+00'::timestamptz, 1, 1, ''),
	(15, 2, 7, '2026-03-01 14:00:00+00'::timestamptz, '2026-03-01 15:00:00+00'::timestamptz, 1, 1, ''),
	(16, 2, 20, '2026-03-01 15:00:00+00'::timestamptz, '2026-03-01 16:00:00+00'::timestamptz, 1, 1, ''),
	(17, 4, 5, '2026-03-01 08:00:00+00'::timestamptz, '2026-03-01 09:00:00+00'::timestamptz, 1, 1, ''),
	(18, 4, 12, '2026-03-01 09:00:00+00'::timestamptz, '2026-03-01 10:00:00+00'::timestamptz, 1, 1, ''),
	(19, 4, 4, '2026-03-01 10:00:00+00'::timestamptz, '2026-03-01 11:00:00+00'::timestamptz, 1, 1, ''),
	(20, 4, 16, '2026-03-01 11:00:00+00'::timestamptz, '2026-03-01 12:00:00+00'::timestamptz, 1, 1, ''),
	(21, 4, 24, '2026-03-01 12:00:00+00'::timestamptz, '2026-03-01 13:00:00+00'::timestamptz, 1, 1, ''),
	(22, 4, 10, '2026-03-01 13:00:00+00'::timestamptz, '2026-03-01 14:00:00+00'::timestamptz, 1, 1, ''),
	(23, 4, 1, '2026-03-01 14:00:00+00'::timestamptz, '2026-03-01 15:00:00+00'::timestamptz, 1, 1, ''),
	(24, 7, 11, '2026-03-01 08:00:00+00'::timestamptz, '2026-03-01 09:00:00+00'::timestamptz, 1, 1, ''),
	(25, 7, 22, '2026-03-01 09:00:00+00'::timestamptz, '2026-03-01 10:00:00+00'::timestamptz, 1, 1, ''),
	(26, 7, 3, '2026-03-01 10:00:00+00'::timestamptz, '2026-03-01 11:00:00+00'::timestamptz, 1, 1, ''),
	(27, 7, 17, '2026-03-01 11:00:00+00'::timestamptz, '2026-03-01 12:00:00+00'::timestamptz, 1, 1, ''),
	(28, 7, 19, '2026-03-01 12:00:00+00'::timestamptz, '2026-03-01 13:00:00+00'::timestamptz, 1, 1, ''),
	(29, 8, 9, '2026-03-01 08:00:00+00'::timestamptz, '2026-03-01 09:00:00+00'::timestamptz, 1, 1, '');

ALTER SEQUENCE public.role_id_seq RESTART WITH 100;
ALTER SEQUENCE public.grade_id_seq RESTART WITH 100;
ALTER SEQUENCE public.location_id_seq RESTART WITH 100;
ALTER SEQUENCE public.user_id_seq RESTART WITH 100;
ALTER SEQUENCE public.employee_id_seq RESTART WITH 100;
ALTER SEQUENCE public.priority_id_seq RESTART WITH 100;
ALTER SEQUENCE public.task_status_id_seq RESTART WITH 100;
ALTER SEQUENCE public.task_type_id_seq RESTART WITH 100;
ALTER SEQUENCE public.agent_point_id_seq RESTART WITH 100;
ALTER SEQUENCE public.agent_point_manager_id_seq RESTART WITH 100;
ALTER SEQUENCE public.agent_point_event_id_seq RESTART WITH 1000;
ALTER SEQUENCE public.task_id_seq RESTART WITH 100;
ALTER SEQUENCE public.task_carryover_id_seq RESTART WITH 100;
