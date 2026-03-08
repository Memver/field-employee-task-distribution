import { createFileRoute } from "@tanstack/react-router";

import useAuth from "@/hooks/useAuth";
import { LoadingButton } from "@/components/ui/loading-button";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
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

function Dashboard() {
  const { user: currentUser } = useAuth();
  const position = [51.505, -0.09];

  return (
    <div>
      <div className="flex flex-col items-start gap-4">
        <h1 className="text-2xl truncate max-w-sm opacity-70 text-[#001F5A]">
          Сотрудники
        </h1>
        {/* <LoadingButton type="submit">Сформировать отчет</LoadingButton> */}
        {/* <div>"Карусель сотрудников"</div> */}
        <div style={{ height: "400px", width: "600px", marginTop: "20px" }}>
          <MapContainer
            style={{ height: "100%", width: "100%" }}
            center={position}
            zoom={13}
            scrollWheelZoom={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={position}>
              <Popup>
                A pretty CSS3 popup. <br /> Easily customizable.
              </Popup>
            </Marker>
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
