// Dummy users for testing authentication
export const dummyUsers = [
  {
    id: 'CU001',
    fullName: 'Feri Hussen',
    email: 'customer@example.com',
    password: 'password123',
    role: 'customer',
    phone: '+62 812-3456-7890',
    birthDate: '1985-04-12',
    address: 'Jl. Sudirman No. 123, Jakarta Pusat, DKI Jakarta 10220',
    policyNumber: 'P001',
    participantNumber: 'PA001',
    insuranceComp: 'PT XYZ Asuransi',
    policyType: 'Asuransi Kesehatan Platinum',
    avatar: '../images/user-avatar-32.png'
  },
  {
    id: 2,
    fullName: 'Opet Ganteng',
    email: 'approver@example.com',
    password: 'password123',
    role: 'approver',
    phone: '+62 812-9876-5432',
    birthDate: '1980-08-15',
    address: 'Jl. Thamrin No. 456, Jakarta Pusat, DKI Jakarta 10350',
    policyNumber: 'A001',
    participantNumber: 'AP001',
    insuranceComp: 'PT XYZ Asuransi',
    policyType: 'Staff Internal',
    avatar: '../images/user-avatar-32.png'
  },
]

// Function to authenticate user
export const authenticateUser = (email, password) => {
  const user = dummyUsers.find(u => u.email === email && u.password === password)
  if (user) {
    // Don't return password in the user object
    const { password: _, ...userWithoutPassword } = user
    return userWithoutPassword
  }
  return null
}

// Function to get user by ID
export const getUserById = (id) => {
  const user = dummyUsers.find(u => u.id === id)
  if (user) {
    const { password: _, ...userWithoutPassword } = user
    return userWithoutPassword
  }
  return null
}