import { useState, useEffect } from "react";
import API from "../api/axios";

export default function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [amount, setAmount] = useState("");

  useEffect(() => {
    API.get("/expenses/").then((res) => setExpenses(res.data));
  }, []);

  const addExpense = async (e) => {
    e.preventDefault();
    await API.post("/expenses/", { amount });
    setAmount("");
    const res = await API.get("/expenses/");
    setExpenses(res.data);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Your Expenses</h2>
      <form onSubmit={addExpense} className="flex gap-2 mb-4">
        <input
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Amount"
          className="p-2 border rounded"
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded">Add</button>
      </form>
      <ul className="bg-white shadow rounded p-4">
        {expenses.map((e) => (
          <li key={e.id} className="flex justify-between border-b py-2">
            <span>${e.amount}</span>
            <span className="text-sm text-gray-500">{e.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

