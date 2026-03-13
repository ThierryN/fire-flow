# Skill: Async/Await Patterns

**Category:** Common Tasks
**Difficulty:** Beginner–Intermediate
**Applies to:** JavaScript, Node.js

---

## The Problem

JavaScript is non-blocking — it doesn't wait for slow things (database calls, API calls, file reads) before moving to the next line. Without proper async handling, you get empty data, race conditions, and crashes that are hard to debug.

---

## The Evolution (Why Async/Await Exists)

```js
// 1. Callbacks — original approach, gets messy fast
getUser(id, function(err, user) {
  getPosts(user.id, function(err, posts) {
    getComments(posts[0].id, function(err, comments) {
      // "callback hell" — deeply nested, hard to read
    });
  });
});

// 2. Promises — better, but still chained
getUser(id)
  .then(user => getPosts(user.id))
  .then(posts => getComments(posts[0].id))
  .catch(err => console.error(err));

// 3. Async/Await — reads like normal code
async function loadData(id) {
  const user = await getUser(id);
  const posts = await getPosts(user.id);
  const comments = await getComments(posts[0].id);
  return comments;
}
```

---

## Pattern 1: Basic Async Function

```js
// Always use try/catch with await
async function getUser(id) {
  try {
    const result = await db.query('SELECT * FROM users WHERE id = $1', [id]);
    return result.rows[0];
  } catch (err) {
    console.error('getUser failed:', err.message);
    throw err; // re-throw so the caller knows it failed
  }
}

// Calling an async function
const user = await getUser(42);
```

---

## Pattern 2: Run Tasks in Parallel

When tasks don't depend on each other, run them at the same time:

```js
// SLOW — runs one after the other (total: 3 seconds)
const user = await fetchUser(id);       // 1 second
const posts = await fetchPosts(id);     // 1 second
const stats = await fetchStats(id);     // 1 second

// FAST — runs all at once (total: ~1 second)
const [user, posts, stats] = await Promise.all([
  fetchUser(id),
  fetchPosts(id),
  fetchStats(id),
]);
```

Use `Promise.all` whenever the tasks are independent. If one fails, the whole thing fails.

---

## Pattern 3: Run Tasks in Parallel, Handle Individual Failures

```js
// Promise.allSettled — each result tells you if it succeeded or failed
const results = await Promise.allSettled([
  fetchUser(id),
  fetchPosts(id),
  fetchStats(id),
]);

const [userResult, postsResult, statsResult] = results;

if (userResult.status === 'fulfilled') {
  console.log(userResult.value); // the data
} else {
  console.error(userResult.reason); // the error
}
```

---

## Pattern 4: Async in a Loop

```js
// WRONG — all start at once, order not guaranteed
const userIds = [1, 2, 3];
userIds.forEach(async (id) => {
  const user = await getUser(id); // forEach doesn't await
  console.log(user);
});

// CORRECT — sequential (one at a time)
for (const id of userIds) {
  const user = await getUser(id);
  console.log(user);
}

// CORRECT — parallel (all at once, faster)
const users = await Promise.all(userIds.map(id => getUser(id)));
```

---

## Pattern 5: Timeout a Slow Request

```js
function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Timed out after ${ms}ms`)), ms)
  );
  return Promise.race([promise, timeout]);
}

// Usage
const user = await withTimeout(fetchUser(id), 5000); // fail after 5 seconds
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `await` outside an `async` function | Mark the function as `async` |
| Forgetting `await` before a promise | Add `await` — you're reading the promise object, not the result |
| Using `forEach` with `async` | Use `for...of` or `Promise.all` instead |
| No `try/catch` around `await` | Wrap in try/catch or the error crashes the process |
| Sequential awaits when parallel is fine | Use `Promise.all` for independent tasks |

---

*Fire Flow Skills Library — MIT License*
