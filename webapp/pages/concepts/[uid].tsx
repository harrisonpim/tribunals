import { useRouter } from "next/router";

export default function Page({ concept, documents }) {
  const router = useRouter();
  const { uid } = router.query;

  return (
    <div>
      <h1>{concept.preferred_label}</h1>
      <p>{concept.description}</p>
      <h2>Matching documents</h2>
      <div>
        <ul>
          {documents.map((document) => (
            <li key={document.id}>
              <a href={`/documents/${document.id}`}>{document.title}</a>
            </li>
          ))}
        </ul>
        {/* link to see a complete list */}
        <a href={`/concepts=${uid}`}>See all</a>
      </div>
    </div>
  );
}

export const getServerSideProps = async (context) => {
  // get the uid from the context
  const { uid } = context.query;
  // fetch the data for the concept with the uid
  const concept = await fetch(`http://localhost:8000/concepts/${uid}`).then(
    (res) => res.json()
  );

  // get a few matching documents too
  const documents = await fetch(
    `http://localhost:8000/documents?concepts=${uid}`
  ).then((res) => res.json().then((data) => data.results));

  // return the concept as a prop
  return {
    props: {
      concept,
      documents,
    },
  };
};
