import React from 'react'

const Header = () => {
  return (
    <div
      style={{
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333',
        textAlign: 'center',
        padding: '20px',
        backgroundColor: '#f0f0f0',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
      }}
    >
      Regulations Dependency Force-Graph
    </div>
  )
}

export default Header
