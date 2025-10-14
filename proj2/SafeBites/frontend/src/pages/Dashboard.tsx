import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="logo">
          <img src="/wolfLogo.png" alt="SafeBites Logo" className="logo-img" />
          <h1>SafeBites</h1>
        </div>
        <button 
          className="btn-logout"
          onClick={() => navigate('/')}
        >
          Log Out
        </button>
      </header>
      
      <main className="dashboard-main">
        <h2>Dashboard</h2>
        <p>Welcome to SafeBites Dashboard!</p>
        <p>This page is under construction.</p>
        
        <div className="dashboard-nav">
          <button onClick={() => navigate('/menu')}>Menu</button>
          <button onClick={() => navigate('/cart')}>Cart</button>
          <button onClick={() => navigate('/reorder')}>Reorder</button>
          <button onClick={() => navigate('/settings')}>Settings</button>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;