import './RestaurantMenu.css';

interface RestaurantMenuProps {
  restaurant: {
    _id: string;
    name: string;
    location: string;
    cuisine: string[];
    rating: number;
  };
  isOpen: boolean;
  onClose: () => void;
}

function RestaurantMenu({ restaurant, isOpen, onClose }: RestaurantMenuProps) {
  if (!isOpen) return null;

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-content" onClick={(e) => e.stopPropagation()}>
        <button className="popup-close-btn" onClick={onClose}>
          ✕
        </button>
        
        <h2 className="popup-title">Restaurant Menu</h2>
        <p className="popup-restaurant-name">{restaurant.name}</p>
        <p className="popup-message">Work in progress</p>
      </div>
    </div>
  );
}

export default RestaurantMenu;