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
	(1, 'Краснодар, Красная, д. 139', 45.0449862, 38.9765876),
    (2, 'Краснодар, В.Н. Мачуги, 41', 45.0128578, 39.0717488),
    (3, 'Краснодар, Красных Партизан, 321', 45.0514211, 38.9564249);

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
	(9, 1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$Cr2d+zOfstb+PKyeE4mQ+w$FDbg5dHzox+LloOT4IM1h5BWZ4q+WZ5CWSGURU2DDwA', 'a', 'a', 'a', true);

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
	
ALTER SEQUENCE public.role_id_seq RESTART WITH 100;
ALTER SEQUENCE public.grade_id_seq RESTART WITH 100;
ALTER SEQUENCE public.location_id_seq RESTART WITH 100;
ALTER SEQUENCE public.user_id_seq RESTART WITH 100;
ALTER SEQUENCE public.employee_id_seq RESTART WITH 100;