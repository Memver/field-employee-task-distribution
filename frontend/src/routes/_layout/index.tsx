import { createFileRoute } from "@tanstack/react-router";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  Polyline,
} from "react-leaflet";
import useAuth from "@/hooks/useAuth";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import { useSuspenseQuery } from "@tanstack/react-query";
import { TasksService } from "@/client";
import { renderToString } from "react-dom/server";
import { ChevronRight } from "lucide-react";
import { Link as RouterLink, useRouterState } from "@tanstack/react-router";
import { LoadingButton } from "@/components/ui/loading-button";

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - FastAPI Cloud",
      },
    ],
  }),
});

function getTasksQueryOptions() {
  return {
    queryFn: () => TasksService.readTasksMe({ skip: 0, limit: 100 }),
    queryKey: ["tasks"],
  };
}

function createNumberedIcon(index: number) {
  // Создаем HTML для кастомного маркера
  const html = renderToString(
    <div className="relative">
      {/* Стандартный маркер Leaflet */}
      <img src={icon} alt="marker" className="w-6 h-10 brightness-0" />
      {/* Номер поверх маркера */}
      <div className="absolute top-1 left-1/2 transform -translate-x-1/2 text-white font-bold text-xs bg-black rounded-full w-4 h-4 flex items-center justify-center">
        {index}
      </div>
    </div>,
  );

  // Создаем divIcon с кастомным HTML
  return L.divIcon({
    html: html,
    className: "custom-marker", // пустой класс, чтобы не добавлять лишние стили
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41],
  });
}

function parseLineString(wktString: string): [number, number][] {
  if (!wktString) return [];

  // Удаляем "LINESTRING (" в начале и ")" в конце
  const coordinatesStr = wktString
    .replace("LINESTRING (", "")
    .replace(")", "")
    .trim();

  // Разбиваем на пары координат
  const pairs = coordinatesStr.split(", ");

  // Преобразуем каждую пару в [lat, lon] (Leaflet использует [lat, lon])
  return pairs.map((pair) => {
    const [lon, lat] = pair.split(" ").map(Number);
    return [lat, lon] as [number, number];
  });
}
function FieldEmployeeDashboard() {
  const { data: data } = useSuspenseQuery(getTasksQueryOptions());

  if (!data || !data.tasks || data.route == "GEOMETRYCOLLECTION EMPTY") {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <p className="text-gray-500 text-lg">Нет данных о маршруте</p>
          <p className="text-gray-400 text-sm mt-2">
            Информация о начальной точке отсутствует
          </p>
        </div>
      </div>
    );
  }

  const position = [data.start_location.lat, data.start_location.lon];

  const routePoints = data?.route ? parseLineString(data.route) : [];

  // Опции для линии маршрута
  const routeOptions = {
    color: "#1de81c", // синий цвет
    weight: 4,
    opacity: 0.7,
    lineCap: "round" as const,
    lineJoin: "round" as const,
  };

  return (
    <div>
      <style>
        {`
          .leaflet-attribution-flag {
            display: none !important;
          }
        `}
      </style>
      <div className="flex flex-col items-start gap-4">
        <div className="flex justify-center w-full">
          <div
            className="rounded-xl overflow-hidden shadow-lg"
            style={{ height: "600px", width: "326px", marginTop: "20px" }}
          >
            <MapContainer
              style={{ height: "100%", width: "100%" }}
              center={position}
              zoom={12}
              scrollWheelZoom={false}
            >
              <TileLayer
                attribution='<a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {routePoints.length > 0 && (
                <Polyline positions={routePoints} pathOptions={routeOptions} />
              )}
              {data.tasks.map((task, index) => (
                <Marker
                  key={task.id}
                  position={[
                    task.agent_point.location.lat,
                    task.agent_point.location.lon,
                  ]}
                  icon={createNumberedIcon(index + 1)}
                >
                  <Popup>
                    <div className="font-semibold">{task.id || "Задача"}</div>
                  </Popup>
                </Marker>
              ))}

              <Marker position={position} icon={createNumberedIcon(0)}></Marker>
            </MapContainer>
          </div>
          {/* <h1 className="text-2xl truncate max-w-sm opacity-70 text-[#001F5A]">
          Сотрудники
        </h1> */}
          {/* <LoadingButton type="submit">Сформировать отчет</LoadingButton> */}
          {/* <div>"Карусель сотрудников"</div> */}
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const { user: currentUser } = useAuth();

  if (currentUser?.role === "EMPLOYEE_MANAGER") {
    return (
      <div className="flex flex-col items-start gap-10 text-xl">
        <RouterLink to="/admin" className="flex items-center gap-2">
          <ChevronRight />
          Пользователи
        </RouterLink>
        <RouterLink to="/locations" className="flex items-center gap-2">
          <ChevronRight />
          Локации
        </RouterLink>
        <RouterLink to="/employees" className="flex items-center gap-2">
          <ChevronRight />
          Выездные сотрудники
        </RouterLink>
        <RouterLink to="/agent-points" className="flex items-center gap-2">
          <ChevronRight />
          Точки
        </RouterLink>
        <RouterLink to="/task-types" className="flex items-center gap-2">
          <ChevronRight />
          Справочники
        </RouterLink>
        <RouterLink to="/tasks" className="flex items-center gap-2">
          <ChevronRight />
          Задачи
        </RouterLink>
        <LoadingButton type="submit">Распределить задачи</LoadingButton>
      </div>
    );
  }
  if (currentUser?.role === "FIELD_EMPLOYEE") {
    return <FieldEmployeeDashboard />;
  }

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="text-center">
        <p className="text-gray-500 text-lg">Нет данных о маршруте</p>
        <p className="text-gray-400 text-sm mt-2">
          Информация о начальной точке отсутствует
        </p>
      </div>
    </div>
  );
}
