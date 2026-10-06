import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(
    () => !!sessionStorage.getItem("accessToken")
  );
  const [showAddForm, setShowAddForm] = useState(false);
  const [website, setWebsite] = useState("");
  const [vaultUsername, setVaultUsername] = useState("");
  const [vaultPassword, setVaultPassword] = useState("");
  const [vaultEntries, setVaultEntries] = useState([]);
  const [visiblePasswords, setVisiblePasswords] = useState({});
  const [editingEntry, setEditingEntry] = useState(null);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoadingVault, setIsLoadingVault] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  useEffect(() => {
    const loadVault = async () => {
      if (!isLoggedIn) return;
      setIsLoadingVault(true); 
      const token = sessionStorage.getItem("accessToken");
  
      try {
        const response = await fetch("http://127.0.0.1:8000/api/vault", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        if (response.status === 401) {
          sessionStorage.removeItem("accessToken");
          setIsLoggedIn(false);
          setVaultEntries([]);
          return;
        }
        
        if (!response.ok) {
          console.error("Could not load vault.");
          return;
        }
  
        const data = await response.json();
        setVaultEntries(data);
      } catch (error) {
        console.error("Could not connect to SecureVault server.", error);
      } finally {
        setIsLoadingVault(false);
      }
    };
  
    loadVault();
  }, [isLoggedIn]);
  const handleSubmit = async (event) => {
    event.preventDefault();
  
    setMessage(
      isRegistering ? "Creating account..." : "Signing in..."
    );
  
    const endpoint = isRegistering
      ? "http://127.0.0.1:8000/api/register"
      : "http://127.0.0.1:8000/api/login";
  
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });
  
      const data = await response.json();
  
      if (!response.ok) {
        setMessage(data.detail || "Something went wrong");
        return;
      }
  
      if (isRegistering) {
        setMessage("Account created! You can now sign in.");
        setIsRegistering(false);
        setPassword("");
      } else {
        sessionStorage.setItem("accessToken", data.access_token);
        setMessage("");
        setIsLoggedIn(true);
      }
    } catch (error) {
      console.error(error);
      setMessage("Could not connect to SecureVault server.");
    }
  };

  const handleSavePassword = async () => {
    const token = sessionStorage.getItem("accessToken");
  
    if (!website || !vaultUsername || !vaultPassword) {
      alert("Please fill in all fields.");
      return;
    }
  
    setIsSaving(true);
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/vault", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          website: website,
          username: vaultUsername,
          password: vaultPassword,
        }),
      });
  
      const data = await response.json();

      if (response.status === 401) {
        sessionStorage.removeItem("accessToken");
        setIsLoggedIn(false);
        setVaultEntries([]);
        alert("Your session has expired. Please sign in again.");
        return;
      }
      
      if (!response.ok) {
        alert(data.detail || "Could not save password.");
        return;
      }
  
      setVaultEntries((currentEntries) => [
        ...currentEntries,
        {
          id: data.id,
          website: data.website,
          username: data.username,
          password: data.password,
        },
      ]);
  
      setWebsite("");
      setVaultUsername("");
      setVaultPassword("");
      setShowNewPassword(false);
      setShowAddForm(false);
  
      alert("Password saved securely!");
    } catch (error) {
      console.error(error);
      alert("Could not connect to SecureVault server.");
    } finally {
      setIsSaving(false);
    }
  };
  const handleDeletePassword = async (entryId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this password?"
    );
  
    if (!confirmed) return;
  
    const token = sessionStorage.getItem("accessToken");
    setDeletingId(entryId);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/vault/${entryId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
  
      const data = await response.json();
      if (response.status === 401) {
        sessionStorage.removeItem("accessToken");
        setIsLoggedIn(false);
        setVaultEntries([]);
        setVisiblePasswords({});
        alert("Your session has expired. Please sign in again.");
        return;
      } 
      if (!response.ok) {
        alert(data.detail || "Could not delete password.");
        return;
      }
  
      setVaultEntries((currentEntries) =>
        currentEntries.filter((entry) => entry.id !== entryId)
      );
      
      setVisiblePasswords((current) => {
        const updated = { ...current };
        delete updated[entryId];
        return updated;
      });
    } catch (error) {
      console.error(error);
      alert("Could not connect to SecureVault server.");
    } finally {
      setDeletingId(null);
    }
  };
  const handleUpdatePassword = async () => {
    if (!editingEntry) return;
  
    const token = sessionStorage.getItem("accessToken");
  
    if (
      !editingEntry.website ||
      !editingEntry.username ||
      !editingEntry.password
    ) {
      alert("Please fill in all fields.");
      return;
    }
  
    setIsUpdating(true);
  
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/vault/${editingEntry.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            website: editingEntry.website,
            username: editingEntry.username,
            password: editingEntry.password,
          }),
        }
      );
  
      const data = await response.json();
      if (response.status === 401) {
        sessionStorage.removeItem("accessToken");
        setIsLoggedIn(false);
        setVaultEntries([]);
        setEditingEntry(null);
        alert("Your session has expired. Please sign in again.");
        return;
      } 
      if (!response.ok) {
        alert(data.detail || "Could not update password.");
        return;
      }
  
      setVaultEntries((currentEntries) =>
        currentEntries.map((entry) =>
          entry.id === editingEntry.id ? data : entry
        )
      );
  
      setEditingEntry(null);
  
      alert("Password updated successfully!");
    } catch (error) {
      console.error(error);
      alert("Could not connect to SecureVault server.");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleGeneratePassword = async () => {
    const token = sessionStorage.getItem("accessToken");
  
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/generate-password?length=20&include_numbers=true&include_symbols=true",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
  
      const data = await response.json();
      if (response.status === 401) {
        sessionStorage.removeItem("accessToken");
        setIsLoggedIn(false);
        setVaultEntries([]);
        setVaultPassword("");
        alert("Your session has expired. Please sign in again.");
        return;
      } 
      if (!response.ok) {
        alert(data.detail || "Could not generate password.");
        return;
      }
  
      setVaultPassword(data.password);
    } catch (error) {
      console.error(error);
      alert("Could not connect to SecureVault server.");
    }
  };
  const filteredEntries = vaultEntries.filter((entry) => {
    const search = searchTerm.toLowerCase();
  
    return (
      entry.website.toLowerCase().includes(search) ||
      entry.username.toLowerCase().includes(search)
    );
  });
  if (isLoggedIn) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <div>
            <h1>🔐 SecureVault</h1>
            <p>Your encrypted password vault</p>
          </div>
          
          <button
            className="logout-button"
            onClick={() => {
              sessionStorage.removeItem("accessToken");
              setIsLoggedIn(false);
              setVaultEntries([]);
              setVisiblePasswords({});
              setEditingEntry(null);
              setVaultPassword("");
              setPassword("");
              setSearchTerm("");
            }}
          >
            Log Out
          </button>
        </div>
  
        <div className="vault-container">
          <div className="vault-title">
            <div>
            <h2>My Passwords</h2>
<p>
  {vaultEntries.length === 0
    ? "No passwords saved yet."
    : `${vaultEntries.length} ${
        vaultEntries.length === 1 ? "password" : "passwords"
      } saved`}
</p>
            </div>

            <div className="vault-search">
  <input
    type="text"
    className="search-input"
    placeholder="Search passwords..."
    value={searchTerm}
    onChange={(event) => setSearchTerm(event.target.value)}
  />
</div>
            
            <button onClick={() => setShowAddForm(true)}>
  + Add Password
</button>
          </div>

          {showAddForm && (
  <div className="add-password-form">
    <h3>Add Password</h3>

    <div className="form-group">
      <label>Website</label>
      <input
        type="text"
        placeholder="example.com"
        value={website}
        onChange={(event) => setWebsite(event.target.value)}
      />
    </div>

    <div className="form-group">
      <label>Username / Email</label>
      <input
        type="text"
        placeholder="username@example.com"
        value={vaultUsername}
        onChange={(event) => setVaultUsername(event.target.value)}
      />
    </div>

    <div className="form-group">
      <label>Password</label>
      <input
  type={showNewPassword ? "text" : "password"}
  placeholder="Enter password"
  value={vaultPassword}
  onChange={(event) => setVaultPassword(event.target.value)}
/>
<button
  type="button"
  onClick={() => setShowNewPassword(!showNewPassword)}
>
  {showNewPassword ? "Hide Password" : "Show Password"}
</button>
      <button
  type="button"
  onClick={handleGeneratePassword}
>
  Generate Secure Password
</button>
    </div>

    <div className="form-actions">
    <button
  type="button"
  onClick={handleSavePassword}
  disabled={isSaving}
>
  {isSaving ? "Saving..." : "Save Password"}
</button>

      <button
        type="button"
        className="cancel-button"
        onClick={() => {
          setShowAddForm(false);
          setWebsite("");
          setVaultUsername("");
          setVaultPassword("");
          setShowNewPassword(false);
        }}
      >
        Cancel
      </button>
    </div>
  </div>
)}

{editingEntry && (
  <div className="add-password-form">
    <h3>Edit Password</h3>

    <div className="form-group">
      <label>Website</label>
      <input
        type="text"
        value={editingEntry.website}
        onChange={(event) =>
          setEditingEntry({
            ...editingEntry,
            website: event.target.value,
          })
        }
      />
    </div>

    <div className="form-group">
      <label>Username / Email</label>
      <input
        type="text"
        value={editingEntry.username}
        onChange={(event) =>
          setEditingEntry({
            ...editingEntry,
            username: event.target.value,
          })
        }
      />
    </div>

    <div className="form-group">
      <label>Password</label>
      <input
        type="password"
        value={editingEntry.password || ""}
        onChange={(event) =>
          setEditingEntry({
            ...editingEntry,
            password: event.target.value,
          })
        }
      />
    </div>

    <div className="form-actions">
    <button
  type="button"
  onClick={handleUpdatePassword}
  disabled={isUpdating}
>
  {isUpdating ? "Saving..." : "Save Changes"}
</button>

      <button
        type="button"
        className="cancel-button"
        onClick={() => {
          setVisiblePasswords((current) => {
            const updated = { ...current };
        
            if (editingEntry) {
              delete updated[editingEntry.id];
            }
        
            return updated;
          });
        
          setEditingEntry(null);
        }}
      >
        Cancel
      </button>
    </div>
  </div>
)}

{isLoadingVault ? (
  <div className="empty-vault">
    <div className="empty-icon">⏳</div>
    <h3>Loading your vault...</h3>
    <p>Retrieving your saved passwords securely.</p>
  </div>
) : vaultEntries.length === 0 ? (
  <div className="empty-vault">
    <div className="empty-icon">🔒</div>
    <h3>Your vault is empty</h3>
    <p>Add your first password to SecureVault.</p>
  </div>
) : filteredEntries.length === 0 ? (
  <div className="empty-vault">
    <div className="empty-icon">🔎</div>
    <h3>No passwords found</h3>
    <p>Try a different website or username.</p>
  </div>
) : (
  <div className="vault-list">
   {filteredEntries.map((entry) => (
      <div className="vault-entry" key={entry.id}>
        <div>
          <h3>{entry.website}</h3>
          <p>{entry.username}</p>
        </div>

        <div>
  <strong>Password:</strong>{" "}
  <span>
    {visiblePasswords[entry.id]
      ? entry.password
      : "••••••••••••"}
  </span>
  
  <button
    type="button"
    onClick={() =>
      setVisiblePasswords((current) => ({
        ...current,
        [entry.id]: !current[entry.id],
      }))
    }
  >
    {visiblePasswords[entry.id] ? "Hide" : "Show"}
  </button>
</div>
<button
  type="button"
  onClick={() => setEditingEntry(entry)}
>
  Edit
</button>
<button
  type="button"
  onClick={() => handleDeletePassword(entry.id)}
  disabled={deletingId === entry.id}
>
  {deletingId === entry.id ? "Deleting..." : "Delete"}
</button>
      </div>
    ))}
  </div>
)}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="login-card">
        <div className="logo">🔐</div>

        <h1>SecureVault</h1>
        <p className="subtitle">
  {isRegistering
    ? "Create your SecureVault account"
    : "Secure access to your passwords"}
</p>

<form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button type="submit">
  {isRegistering ? "Create Account" : "Sign In"}
</button>
        </form>

        {message && <p className="register-text">{message}</p>}

        <p className="register-text">
  {isRegistering ? "Already have an account? " : "Don't have an account? "}

  <a
    href="#"
    onClick={(event) => {
      event.preventDefault();
      setIsRegistering(!isRegistering);
      setMessage("");
    }}
  >
    {isRegistering ? "Sign in" : "Create account"}
  </a>
</p>
      </div>
    </div>
  );
}

export default App;