const Input = ({ value, onChange, placeholder, className = "" }) => {
    return (
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full p-2 bg-gray-700 text-white border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      />
    );
  };
  
  export default Input;