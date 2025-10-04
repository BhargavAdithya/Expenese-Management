// import { useState, useEffect } from "react";
// import API from "../api/axios";
// import React from "react";

// export default function Dashboard() {
//   const [expenses, setExpenses] = useState([]);
//   const [amount, setAmount] = useState("");

//   useEffect(() => {
//     API.get("/expenses/").then((res) => setExpenses(res.data));
//   }, []);

//   const addExpense = async (e) => {
//     e.preventDefault();
//     await API.post("/expenses/", { amount });
//     setAmount("");
//     const res = await API.get("/expenses/");
//     setExpenses(res.data);
//   };

//   return (
//     <div>
//       <h2 className="text-xl font-bold mb-4">Your Expenses</h2>
//       <form onSubmit={addExpense} className="flex gap-2 mb-4">
//         <input
//           value={amount}
//           onChange={(e) => setAmount(e.target.value)}
//           placeholder="Amount"
//           className="p-2 border rounded"
//         />
//         <button className="bg-blue-600 text-white px-4 py-2 rounded">Add</button>
//       </form>
//       <ul className="bg-white shadow rounded p-4">
//         {expenses.map((e) => (
//           <li key={e.id} className="flex justify-between border-b py-2">
//             <span>${e.amount}</span>
//             <span className="text-sm text-gray-500">{e.status}</span>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// }

import { useState, useEffect } from "react";
import API from "../api/axios";
import React from "react";

export default function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [date, setDate] = useState("");

  // Fetch expenses on mount
  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const res = await API.get("/expenses/");
      setExpenses(res.data.expenses || []); // match backend structure
    } catch (err) {
      console.error("Error fetching expenses:", err.response?.data || err.message);
    }
  };

  const addExpense = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        amount: parseFloat(amount),
        original_currency: currency,
        category,
        expense_date: date,
      };

      await API.post("/expenses/", payload);
      setAmount("");
      setCategory("");
      setDate("");
      await fetchExpenses(); // refresh list after adding
    } catch (err) {
      console.error("Error adding expense:", err.response?.data || err.message);
      alert(err.response?.data?.error || "Failed to add expense");
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Your Expenses</h2>

      <form onSubmit={addExpense} className="flex flex-col gap-2 mb-4">
        <input
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Amount"
          type="number"
          className="p-2 border rounded"
          required
        />
        <input
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="Category"
          className="p-2 border rounded"
          required
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="p-2 border rounded"
          required
        />
        <select
          value={currency}
          onChange={(e) => setCurrency(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="USD">USD</option>
          <option value="INR">INR</option>
          <option value="EUR">EUR</option>
        </select>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Add
        </button>
      </form>

      <ul className="bg-white shadow rounded p-4">
        {expenses.length > 0 ? (
          expenses.map((e) => (
            <li key={e.id} className="flex justify-between border-b py-2">
              <span>
                ${e.amount} — <span className="italic">{e.category}</span>
              </span>
              <span className="text-sm text-gray-500">{e.status}</span>
            </li>
          ))
        ) : (
          <p className="text-gray-500 text-sm">No expenses yet.</p>
        )}
      </ul>
    </div>
  );
}
