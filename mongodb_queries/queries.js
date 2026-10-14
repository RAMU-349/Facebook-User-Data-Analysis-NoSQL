// Facebook User Data Analysis Using NoSQL
// Database: facebook_analysis
// Collection: facebook_users
// Uses synthetic/anonymized sample data.

// 1. Display all users
db.facebook_users.find();

// 2. Display users aged 18 or above
db.facebook_users.find({ age: { $gte: 18 } });

// 3. Sort users by age in descending order
db.facebook_users.find().sort({ age: -1 });

// 4. Count the total number of users
db.facebook_users.countDocuments();

// 5. Group users by age
db.facebook_users.aggregate([
  {
    $group: {
      _id: "$age",
      totalUsers: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
]);

// 6. Calculate total likes received by each user
db.facebook_users.aggregate([
  {
    $project: {
      name: 1,
      totalLikes: { $sum: "$posts.likes" }
    }
  }
]);

// 7. Count users by city, if the city field exists
db.facebook_users.aggregate([
  {
    $group: {
      _id: "$city",
      totalUsers: { $sum: 1 }
    }
  },
  { $sort: { totalUsers: -1 } }
]);

// 8. Find users with the highest number of followers
db.facebook_users.find().sort({ followers: -1 });

// Note: Field names depend on the actual document structure.
// Run these queries in MongoDB Shell or Compass after checking your data.
