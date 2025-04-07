"use client";

import { useRouter } from "next/navigation"; // Import useRouter for navigation
import { useEffect, useState } from "react"; // Import hooks for client-side data fetching
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

// --- Loading Skeleton Component ---
// (Keep the Skeleton component as it is)
function CustomerTableSkeleton() {
  return (
    <div className="space-y-3">
      {/* Simulate Table Header */}
      <div className="flex justify-between space-x-4 px-4 py-3">
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-5 w-1/4" />
      </div>
      {/* Simulate Table Rows */}
      {[...Array(5)].map((_, i) => (
        <div
          key={i} // Use index for key in skeleton
          className="flex justify-between space-x-4 px-4 py-4 border-t"
        >
          <Skeleton className="h-5 w-1/3" />
          <Skeleton className="h-5 w-1/3" />
          <Skeleton className="h-5 w-1/4" />
        </div>
      ))}
    </div>
  );
}

// --- Main Component ---
export default function Customers() {
  // --- State for data, loading, and error ---
  // Since this is now a Client Component, we manage state with useState
  const [customers, setCustomers] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- useRouter hook ---
  const router = useRouter(); // Initialize the router

  // --- Data Fetching Logic ---
  // Use useEffect to fetch data when the component mounts
  useEffect(() => {
    async function fetchCustomers() {
      setIsLoading(true); // Start loading
      setError(null); // Reset error
      const apiUrl = "http://127.0.0.1:5000/api/customers";

      try {
        // Optional: Simulate network delay
        // await new Promise(resolve => setTimeout(resolve, 1500));

        const res = await fetch(apiUrl);

        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        setCustomers(data); // Set fetched data
      } catch (err) {
        console.error("Failed to fetch customers:", err);
        setError(err.message || "Network error or failed to fetch");
      } finally {
        setIsLoading(false); // Stop loading regardless of success/error
      }
    }

    fetchCustomers();
  }, []); // Empty dependency array means this runs once on mount

  // --- Click Handler ---
  const handleRowClick = (customerId) => {
    // Navigate to the chat page for the specific customer
    router.push(`/chat/${customerId}`);
  };

  // --- Render Logic ---
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-yellow-50 via-orange-50 to-red-100 p-4 md:p-8 flex justify-center items-start">
      <div className="w-full max-w-5xl bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="p-5 border-b border-gray-200 bg-gray-50/50">
          <h2 className="text-xl font-semibold text-gray-700">Customer List</h2>
          <p className="text-sm text-gray-500 mt-1">
            A list of all registered customers. Click a row to chat.
          </p>
        </div>

        <div className="p-0">
          {error ? (
            <div className="p-10 text-center text-red-600">
              <p>Error loading customers: {error}</p>
              <p className="text-sm text-gray-500 mt-2">
                Please try refreshing the page or check the API connection.
              </p>
            </div>
          ) : isLoading ? ( // Check isLoading state
            <CustomerTableSkeleton />
          ) : !customers || customers.length === 0 ? ( // Check if customers array exists and is empty
            <div className="p-10 text-center text-gray-500">
              No customers found.
            </div>
          ) : (
            <Table>
              <TableHeader className="bg-gray-100/80">
                <TableRow>
                  <TableHead className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider min-w-[150px]">
                    Customer Name
                  </TableHead>
                  <TableHead className="px-4 py-3 text-center text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Customer Group
                  </TableHead>
                  <TableHead className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Customer Number
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((customer, index) => (
                  <TableRow
                    key={customer.customer_pk}
                    className="hover:bg-orange-50/50 transition-colors duration-150 ease-in-out cursor-pointer" // Added cursor-pointer for better UX
                    onClick={() => handleRowClick(customer.customer_pk)} // Added onClick handler
                  >
                    <TableCell className="px-4 py-3 font-medium text-gray-800 whitespace-nowrap">
                      {customer.customer_name}
                    </TableCell>
                    <TableCell className="px-4 py-3 text-center text-gray-600">
                      {customer.customer_group}
                    </TableCell>
                    <TableCell className="px-4 py-3 text-right text-gray-600 font-mono text-sm">
                      {customer.customer_pk}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
        {!error && customers && customers.length > 0 && (
          <div className="p-4 border-t border-gray-200 bg-gray-50/50 text-xs text-gray-500">
            Total Customers: {customers.length}
          </div>
        )}
      </div>
    </div>
  );
}

// import {
//   Table,
//   TableBody,
//   TableCaption,
//   TableCell,
//   TableHead,
//   TableHeader,
//   TableRow,
// } from "@/components/ui/table";
// import { Skeleton } from "@/components/ui/skeleton"; // Assuming you have a Skeleton component

// async function getCustomers() {
//   // Using a placeholder URL for demonstration if needed, replace with your actual API
//   // const apiUrl = "https://jsonplaceholder.typicode.com/users"; // Example placeholder
//   const apiUrl = "http://127.0.0.1:5000/api/customers";

//   try {
//     // Simulate network delay for testing loading state (optional)
//     // await new Promise(resolve => setTimeout(resolve, 1500));

//     const res = await fetch(apiUrl);

//     if (!res.ok) {
//       console.error(`API Error: ${res.status} ${res.statusText}`);
//       // Return an error indicator instead of null for better handling
//       return { customers: null, error: `Failed to fetch: ${res.status}` };
//     }

//     const customers = await res.json();
//     // Adapt if your API returns data differently, e.g. if customers are nested
//     // const customers = data.customers || data; // Adjust based on actual API response structure

//     // Map placeholder data structure if using jsonplaceholder example
//     /*
//     const customers = data.map(user => ({
//       customer_pk: user.id,
//       customer_name: user.name,
//       customer_group: user.company.name, // Example mapping
//     }));
//     */

//     return { customers, error: null };
//   } catch (error) {
//     console.error("Failed to fetch customers:", error);
//     return { customers: null, error: error.message || "Network error" };
//   }
// }

// // --- Loading Skeleton Component ---
// // You might place this in a separate file or keep it here if simple
// function CustomerTableSkeleton() {
//   return (
//     <div className="space-y-3">
//       {/* Simulate Table Header */}
//       <div className="flex justify-between space-x-4 px-4 py-3">
//         <Skeleton className="h-5 w-1/3" />
//         <Skeleton className="h-5 w-1/3" />
//         <Skeleton className="h-5 w-1/4" />
//       </div>
//       {/* Simulate Table Rows */}
//       {[...Array(5)].map((_, i) => (
//         <div
//           key={i}
//           className="flex justify-between space-x-4 px-4 py-4 border-t"
//         >
//           <Skeleton className="h-5 w-1/3" />
//           <Skeleton className="h-5 w-1/3" />
//           <Skeleton className="h-5 w-1/4" />
//         </div>
//       ))}
//     </div>
//   );
// }

// export default async function Customers() {
//   // Fetch data *before* rendering potentially, or handle loading state inside
//   // Note: Server Components fetch data before rendering the page.
//   // If this were a Client Component with useEffect, the loading state logic would be different.
//   const { customers, error } = await getCustomers();

//   return (
//     // Use padding on the main container for overall spacing
//     <div className="min-h-screen w-full bg-gradient-to-br from-yellow-50 via-orange-50 to-red-100 p-4 md:p-8 flex justify-center items-start">
//       {/* Card Container */}
//       <div className="w-full max-w-5xl bg-white rounded-xl shadow-lg overflow-hidden">
//         {/* Optional: Card Header */}
//         <div className="p-5 border-b border-gray-200 bg-gray-50/50">
//           <h2 className="text-xl font-semibold text-gray-700">Customer List</h2>
//           <p className="text-sm text-gray-500 mt-1">
//             A list of all registered customers.
//           </p>
//         </div>

//         {/* Conditional Rendering: Error > Loading > Table */}
//         <div className="p-0">
//           {" "}
//           {/* Remove padding here if table has its own */}
//           {error ? (
//             <div className="p-10 text-center text-red-600">
//               <p>Error loading customers: {error}</p>
//               <p className="text-sm text-gray-500 mt-2">
//                 Please try refreshing the page or contact support.
//               </p>
//             </div>
//           ) : !customers ? (
//             // Display Skeleton Loading state
//             // Note: In Server Components, the page waits for data.
//             // A true loading state often involves Suspense or client-side fetching.
//             // This skeleton might only show briefly or if data fetching is slow.
//             <CustomerTableSkeleton />
//           ) : customers.length === 0 ? (
//             <div className="p-10 text-center text-gray-500">
//               No customers found.
//             </div>
//           ) : (
//             <Table>
//               {/* Consider moving caption outside or styling it differently if needed */}
//               {/* <TableCaption className="py-4 text-sm text-gray-500">A list of your customers.</TableCaption> */}
//               <TableHeader className="bg-gray-100/80">
//                 {/* Use sticky header if table might scroll vertically within its container */}
//                 {/* <TableHeader className="bg-gray-100/80 sticky top-0 z-10"> */}
//                 <TableRow>
//                   {/* Adjust widths or use min-w for better responsiveness */}
//                   <TableHead className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider min-w-[150px]">
//                     Customer Name
//                   </TableHead>
//                   <TableHead className="px-4 py-3 text-center text-xs font-medium text-gray-600 uppercase tracking-wider">
//                     Customer Group
//                   </TableHead>
//                   <TableHead className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
//                     Customer Number
//                   </TableHead>
//                 </TableRow>
//               </TableHeader>
//               <TableBody>
//                 {customers.map((customer, index) => (
//                   <TableRow
//                     key={customer.customer_pk}
//                     // Add hover effect and optional zebra striping
//                     className="hover:bg-orange-50/50 transition-colors duration-150 ease-in-out"
//                     // Optional Zebra Striping:
//                     // className={`hover:bg-orange-50/50 transition-colors duration-150 ease-in-out ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50/70'}`}
//                   >
//                     <TableCell className="px-4 py-3 font-medium text-gray-800 whitespace-nowrap">
//                       {customer.customer_name}
//                     </TableCell>
//                     <TableCell className="px-4 py-3 text-center text-gray-600">
//                       {customer.customer_group}
//                     </TableCell>
//                     <TableCell className="px-4 py-3 text-right text-gray-600 font-mono text-sm">
//                       {customer.customer_pk}
//                     </TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>
//           )}
//         </div>
//         {/* Optional: Card Footer */}
//         {!error && customers && customers.length > 0 && (
//           <div className="p-4 border-t border-gray-200 bg-gray-50/50 text-xs text-gray-500">
//             Total Customers: {customers.length}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }
