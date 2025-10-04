import { useEffect, useState } from "react";
import API from "../api/axios";
import React from "react";

export default function Approvals() {
  const [approvals, setApprovals] = useState([]);

  useEffect(() => {
    API.get("/approvals/").then((res) => setApprovals(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Pending Approvals</h2>
      <div className="bg-white p-4 rounded shadow">
        {approvals.map((a) => (
          <div key={a.id} className="flex justify-between py-2 border-b">
            <span>Approval ID: {a.id}</span>
            <span>Status: {a.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

